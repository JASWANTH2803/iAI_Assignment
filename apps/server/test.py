from XAgent.agent.tool_agent.agent import ToolAgent
from XAgent.config import CONFIG
from XAgent.message_history import Message

def agent_factory():
    prompt_messages = [
        Message(role="user", content="{input}")
    ]
    agent = ToolAgent(config=CONFIG, prompt_messages=prompt_messages)
    def agent_chain(inputs):
        prompt = inputs["input"] if isinstance(inputs, dict) else str(inputs)
        response, _ = agent.parse(placeholders={"input": prompt}, functions=[])
        return {"content": response.get("content", "[No response]")}
    return agent_chain

if __name__ == "__main__":
    agent = agent_factory()
    result = agent({"input": "Hello, XAgent!"})
    print("DEBUG: XAgent raw response:", result)
    print(result["content"])
    print(agent({"input": "Hello, XAgent!"}))