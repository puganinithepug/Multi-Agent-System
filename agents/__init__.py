# agents/__init__.py
#from langchain.agents import AgentExecutor, create_react_agent
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from core.llm_factory import get_deepseek, get_qwen

REACT_TEMPLATE = """You are {role}. Use this format:

Question: the input question
Thought: reason about what to do
Action: one of [{tool_names}]
Action Input: JSON input to the tool
Observation: the tool result
...
Thought: I have enough information
Final Answer: the final response

Tools available:
{tools}

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

def build_agent(role: str, model: str, tools: list):
    llm = get_deepseek() if model == "deepseek" else get_qwen()
    prompt = PromptTemplate.from_template(REACT_TEMPLATE)
    agent = create_react_agent(llm, tools)
    return agent
