# Simple XAgent test script
from XAgent.agent.tool_agent.agent import ToolAgent
from XAgent.config import CONFIG
from XAgent.message_history import Message

if __name__ == "__main__":
    prompt = "What is the capital of France?"
    # Use Message class as required by XAgent
    prompt_messages = [
        Message(role="user", content="{input}")
    ]
    agent = ToolAgent(config=CONFIG, prompt_messages=prompt_messages)
    try:
        response, _ = agent.parse(placeholders={"input": prompt}, functions=[])
        print("Prompt:", prompt)
        print("XAgent Response:", response.get("content", "[No response]"))
    except Exception as e:
        print("An error occurred:", e)
