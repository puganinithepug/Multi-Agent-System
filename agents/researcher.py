# agents/researcher.py
from agents import build_agent

def create_researcher(tools: list):
    return build_agent(
        model="qwen",
        tools=tools,
        role = "You are a Researcher. You search local files and the web to answer questions stated by the user with relevant facts."
    )
