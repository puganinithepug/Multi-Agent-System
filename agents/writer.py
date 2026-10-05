# agents/writer.py
from agents import build_agent

def create_writer(tools: list):
    return build_agent(
        role="You are an Writer. You write reports using supporting evidence from research and locally available data.",
        model="dolphin",
        tools=tools,
    )
