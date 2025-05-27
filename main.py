#!/usr/bin/env python3

from google.adk.agents import run_config
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os

from agent import root_agent


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
