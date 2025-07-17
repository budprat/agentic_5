{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import random\
\
from google.adk.agents import Agent\
from google.adk.models.lite_llm import LiteLlm\
\
# https://docs.litellm.ai/docs/providers/openrouter\
model = LiteLlm(\
    model="openrouter/openai/gpt-4.1",\
    api_key=os.getenv("OPENROUTER_API_KEY"),\
)\
\
\
def get_dad_joke():\
    jokes = [\
        "Why did the chicken cross the road? To get to the other side!",\
        "What do you call a belt made of watches? A waist of time.",\
        "What do you call fake spaghetti? An impasta!",\
        "Why did the scarecrow win an award? Because he was outstanding in his field!",\
    ]\
    return random.choice(jokes)\
\
\
root_agent = Agent(\
    name="dad_joke_agent",\
    model=model,\
    description="Dad joke agent",\
    instruction="""\
    You are a helpful assistant that can tell dad jokes. \
    Only use the tool `get_dad_joke` to tell jokes.\
    """,\
    tools=[get_dad_joke],\
)}