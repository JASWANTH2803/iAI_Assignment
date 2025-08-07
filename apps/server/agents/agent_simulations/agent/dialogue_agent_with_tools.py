from typing import List, Optional

from langchain.agents import AgentType, initialize_agent
from langchain.schema import AIMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI

from agents.agent_simulations.agent.dialogue_agent import DialogueAgent
from agents.conversational.output_parser import ConvoOutputParser
from config import Config
from memory.zep.zep_memory import ZepMemory
from services.run_log import RunLogsManager
from typings.agent import AgentWithConfigsOutput


class DialogueAgentWithTools(DialogueAgent):
    def __init__(
        self,
        name: str,
        agent_with_configs: AgentWithConfigsOutput,
        system_message: SystemMessage,
        model: ChatOpenAI,
        tools: List[any],
        session_id: str,
        sender_name: str,
        is_memory: bool = False,
        run_logs_manager: Optional[RunLogsManager] = None,
        **tool_kwargs,
    ) -> None:
        super().__init__(name, agent_with_configs, system_message, model)
        self.tools = tools
        self.session_id = session_id
        self.sender_name = sender_name
        self.is_memory = is_memory
        self.run_logs_manager = run_logs_manager

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """

        memory: ZepMemory

        # FIXME: This is a hack to get the memory working
        # if self.is_memory:
        memory = ZepMemory(
            session_id=self.session_id,
            url=Config.ZEP_API_URL,
            api_key=Config.ZEP_API_KEY,
            memory_key="chat_history",
            return_messages=True,
        )

        memory.human_name = self.sender_name
        memory.ai_name = self.agent_with_configs.agent.name
        memory.auto_save = False
        # else:
        #     memory = ConversationBufferMemory(
        #         memory_key="chat_history", return_messages=True
        #     )

        callbacks = []

        if self.run_logs_manager:
            self.model.callbacks = [self.run_logs_manager.get_agent_callback_handler()]
            callbacks.append(self.run_logs_manager.get_agent_callback_handler())

        # === XAgent Integration ===
        from XAgent.agent.tool_agent.agent import ToolAgent
        from XAgent.config import CONFIG
        from XAgent.message_history import Message

        prompt = "\n".join(self.message_history + [self.prefix])
        prompt_messages = [
            Message(role="user", content="{input}")
        ]
        agent = ToolAgent(config=CONFIG, prompt_messages=prompt_messages)
        try:
            response, _ = agent.parse(placeholders={"input": prompt}, functions=[])
            res = response.get("content", "[No response]")
        except Exception as e:
            res = f"XAgent error: {e}"
        # message = AIMessage(content=res)  # If you still want to wrap in AIMessage
        return res
