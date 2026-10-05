from core.llm_factory import get_deepseek
from core.llm_factory import get_qwen
from langgraph.prebuilt import create_react_agent

# agents/react_agent.py
def build_agent(role: str, model: str, tools: list):
    # 1. Pick the LLM
    llm = get_deepseek() if model == "deepseek" else get_qwen()

    # 2. Create the ReAct Prompt (The "Soul")
    prompt = PromptTemplate.from_template(REACT_TEMPLATE.format(role=role))

    # 3. Combine LLM + Tools + Prompt into an Agent
    agent = create_react_agent(llm, tools, prompt)

    # 4. Wrap it in an Executor (the loop runner)
    return AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)
