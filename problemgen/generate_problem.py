
from openai import OpenAI
from preprocessing.Key import OPENAI_API_KEY
from sympy import symbols, Eq, solve, sympify
from problemgen.WolframAlpha import *
import re

client = OpenAI(api_key=OPENAI_API_KEY)



def generate_equation_rearrangement():
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "user",
          "content": "Please generate an easy equation rearrangement question. Provide the question in LaTeX form, only provide the question - do not provide any other prose, only the mathematical expression. Use `x` as the variable to solve for, do not mention anything else or write any natural language. Please ensure the solution is an integer."
        },
      ],
      temperature=0.7,
      max_tokens=64,
      top_p=1
    )
    return response.choices[0].message.content



def get_answer(problem):
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": f"Take a break, then please calculate the answer to this mathematical expression: {problem}. Please only provide the answer, and only the answer"
      },
    ],
    temperature=0.7,
    max_tokens=64,
    top_p=1
  )
  content = response.choices[0].message.content



def get_explanation(problem, answer):
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": f"Explain in 1 simple sentence how this problem {problem} has this answer {answer}. Explain in simple english, do NOT use latex"
      },
    ],
    temperature=0.7,
    max_tokens=64,
    top_p=1
  )
  content = response.choices[0].message.content
  return content


def program_answer(problem):
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": f"Please program a python script to solve this maths problem: {problem}. Store the result in the `result` variable, as I will be executing this using `exec`. Please only write valid python code, do not write any additional prose."
      },
    ],
    temperature=0.7,
    max_tokens=64,
    top_p=1
  )

  content = response.choices[0].message.content
  content = content.replace("```python", "")
  content = content.replace("```", "")
  print(content)

  exec(content)

  return locals().get('result', None)



if __name__ == '__main__':
  #a = generate_equation_rearrangement()
  #print(a)
  #_a = a.replace("\\[", "")
  #b = program_answer("Solve for x " + _a)
  #print(b)

  c = program_answer("((\lambda x.x)(1))")
  print(c)

  e = get_explanation("((\lambda x.x)(1))", c)
  print(e)

