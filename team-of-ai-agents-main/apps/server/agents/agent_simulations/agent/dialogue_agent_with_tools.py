from typing import List, Optional

from agents.agent_simulations.agent.dialogue_agent import DialogueAgent
from agents.conversational.output_parser import ConvoOutputParser
from config import Config
from memory.zep.zep_memory import ZepMemory
from services.run_log import RunLogsManager
from typings.agent import AgentWithConfigsOutput
# XAgent integration
from XAgent.agent.tool_agent.agent import ToolAgent


class DialogueAgentWithTools(DialogueAgent):
    def __init__(
        self,
        name: str,
        agent_with_configs: AgentWithConfigsOutput,
        system_message,
        model,
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

        callbacks = []

        if self.run_logs_manager:
            self.model.callbacks = [self.run_logs_manager.get_agent_callback_handler()]
            callbacks.append(self.run_logs_manager.get_agent_callback_handler())

        # XAgent ToolAgent integration
        # Adapt tools and memory to XAgent's expected format if needed
        xagent = ToolAgent()
        prompt = "\n".join(self.message_history + [self.prefix])
        xagent_response, _ = xagent.parse(
            placeholders={"input": prompt},
            arguments=None,
            functions=None,
            function_call=None,
            stop=None,
            additional_messages=[],
            additional_insert_index=-1
        )
        res = xagent_response.get("content", "[XAgent did not return a response]")

        return res
