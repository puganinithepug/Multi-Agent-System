# agents/analyst.py
from agents import build_agent

def create_analyst(tools: list):
    return build_agent(
        role="You are an Analyst. You process data, write Python code, and compare results.",
        model="deepseek",
        tools=tools,
    )
