# A quiz AI

This app is for testing Google's ADK and gemini-2.0-flash. Run the thing by copying .env.template to .env and filling
in the details, then start by simply running `python main.py`.

## Code

The quiz is built using two LLM agents: one for asking the questions, one for checking the answers. Keeping it together
are two non-AI agents. One that inputs the user's answer, and another to print the correction and keep tabs of the
score.

The agents are combined in a LoopAgent, which keep running until the quiz is done.

In order to get varied output, the temperature of the LLM asking the questions is set really high, and it is also
supplied with a few random words as well as randomizing the order in which the topics are presented.

## Example quiz

```
% ./main.py
Quiz started! Type your answers into the terminal.

1. In which country is the world's oldest operating post office located?
Answer> UK   
correct (1/1 correct answers)

2. What element, named after the Swedish village of Ytterby, is used in red television screens?
Answer> Rim
incorrect The correct answer is Yttrium (1/2 correct answers)

3. In which country did the practice of placing a lit candle in a window originate, as a symbol of welcome or safe haven?
Answer> France
incorrect The correct answer is Ireland (1/3 correct answers)

...

12. What is the name of the world's largest desert?
Answer> Sahara
incorrect The correct answer is Antarctic Polar Desert (5/12 correct answers)

Quiz over!
```
