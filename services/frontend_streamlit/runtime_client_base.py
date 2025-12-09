import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    session_id: str
    user_id: str
    message: str = field(default="No response from agent.")


class RuntimeClient(ABC):
    def __init__(self, runtime_name: str) -> None:
        self.runtime_name: str = runtime_name
        logger.info(f"Initialized runtime client for agent: {self.runtime_name}")

    @abstractmethod
    def invoke_agent(
        self,
        message: str,
        user_id: str,
        session_id: str,
    ) -> AgentResponse:
        """Invoke the agent runtime.

        Args:
            message: User's query
            user_id: User identifier
            session_id: Conversation session ID

        Returns:
            An AgentResponse containing the session_id, the user_id,
            and the agent's message

        Raises:
            RuntimeError: If invocation fails
        """
