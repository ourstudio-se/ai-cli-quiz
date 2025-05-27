#!/usr/bin/env python3

from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.agents import run_config
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.events import Event, EventActions
import os
import random

import prompts


NUM_QUESTIONS = 12


def random_word():
    words = [
        'cat', 'dog', 'fish', 'bird', 'computer', 'book', 'car', 'bicycle',
        'tree', 'flower', 'star', 'moon', 'sun', 'lake', 'mountain',
        'school', 'city', 'country', 'river', 'sea', 'kite', 'hammer',
        'lantern', 'moss', 'apple', 'bread', 'bottle', 'chair', 'glove',
        'bramble', 'coin', 'pencil', 'drum', 'curtain', 'window', 'book',
        'stone', 'trumpet', 'tent', 'symphony', 'candle', 'fork', 'brick'
    ]
    random.shuffle(words)
    return ', '.join(words[:4])


def shuffled_topis():
    topics = [
        'geography', 'science', 'non-american history', 'music',
        'technology', 'culture', 'literature', 'film', 'sports',
        'current events', 'general knowledge',
    ]
    random.shuffle(topics)
    return ', '.join(topics)


quizzer = LlmAgent(
    name='quizzer',
    model='gemini-2.0-flash',
    description='Ask an entertaining question for the user to answer.',
    instruction=(
        f'''You are a quiz question generator. Each time you run, generate a fun, interesting and difficult question for the user to answer.
            You must *ALWAYS* return a question that is short and concise, and can be answered with a single word or a short phrase.
            Questions favoring a non-American user are preferred, but not required.

            For variety, use the following reference words for inspiration: {random_word()}. Try to vary the questions as much as possible.

            The question could be about any topic, here are some examples you can use: {shuffled_topis()}.

            State your question:'''
    ),
    generate_content_config=types.GenerateContentConfig(temperature=0.9), # creative
    output_key='quiz_question'
)


answer_checker = LlmAgent(
    name='answer_checker',
    model='gemini-2.0-flash',
    description='Verify if the answer to a quiz question is correct.',
    instruction=prompts.ANSWER_CHECK,
    # generate_content_config=types.GenerateContentConfig(temperature=0.0), # deterministic
    output_key='quiz_correction'
)


class AskAgent(BaseAgent):
    '''Agent that outputs the question and takes user input.'''
    async def _run_async_impl(self, ctx):
        question = ctx.session.state.get('quiz_question', '').strip()
        loop = ctx.session.state.get('loop', 0)
        loop += 1
        ctx.session.state['loop'] = loop
        print(f'{loop}. {question}')

        answer = ''
        while not answer:
            answer = input('Answer> ').strip()
        ctx.session.state['quiz_answer'] = answer
        yield Event(
            author=self.name,
            content=types.Content(role='ask'),
            actions=EventActions()
        )


class OutputAgent(BaseAgent):
    '''Agent that outputs the correction.'''
    async def _run_async_impl(self, ctx):
        # always remove previous data to avoid confusion
        del ctx.session.state['quiz_answer']
        correction = ctx.session.state.get('quiz_correction', '').replace('\n', ' ').strip()
        c = correction.lower()
        if 'incorrect' in c:
            # don't pass on 'incorrect' to agent, it will think it did something wrong
            del ctx.session.state['quiz_correction']
        else:
            ctx.session.state['correct_answers'] = ctx.session.state.get('correct_answers', 0) + 1
        correct_answers = ctx.session.state.get('correct_answers', 0)
        loop = ctx.session.state.get('loop', 0)

        # strip leak from correction if necessary
        leak = 'Your evaluation:'
        idx = correction.find(leak)
        if idx >= 0:
            correction = correction[idx + len(leak):].strip()

        # output
        print(correction, f'({correct_answers}/{loop} correct answers)\n')
        yield Event(
            author=self.name,
            content=types.Content(role='output'),
            actions=EventActions()
        )


asker = AskAgent(name='asker')
outputter = OutputAgent(name='outputter')

root_agent = LoopAgent(
    name='quiz_loop',
    sub_agents=[quizzer, asker, answer_checker, outputter],
    max_iterations=NUM_QUESTIONS,
    description='Run a quiz loop where the user answers questions and receives feedback.',
)


######################################################################


# set the environment variables for ADK
for line in open('.env'):
    k, v = [w.strip() for w in line.split('=')]
    os.environ[k] = v

# Set up runner and session for execution
APP_NAME = 'quiz-app'
USER_ID = 'user-123'
SESSION_ID = 'session-456'
# Create session service and session
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=dict(correct_answers=0)
)
# Create runner
runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service
)

# Run the loop agent using the runner
def run_loop_agent(query):

    print(f'Quiz started! Type your answers into the terminal.\n')

    # Create content from user query
    content = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )
    # Run the agent with the runner
    for event in runner.run(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
            run_config=run_config.RunConfig(response_modalities=['TEXT'])
    ):
        pass

    print(f'Quiz over!')


run_loop_agent('Run quiz!')
