"""AgentCore Runtime client for invoking deployed agents via Frontend Gateway."""

from __future__ import annotations

import logging
from typing import Any

import requests

from services.frontend_streamlit.config import load_config
from services.frontend_streamlit.runtime_client_base import AgentResponse, RuntimeClient

logger = logging.getLogger(__name__)


class AgentCoreRuntimeClient(RuntimeClient):
    """Client for invoking AgentCore Runtime via Frontend Gateway."""

    def __init__(
        self,
        runtime_name: str = "customersupport",
    ):
        """Initialize the runtime client.

        Args:
            runtime_name: Name of the AgentCore runtime
        """
        super().__init__(runtime_name=runtime_name)

    def invoke_agent(
        self,
        message: str,
        user_id: str,
        session_id: str,
    ) -> AgentResponse:
        """Invoke the AgentCore Runtime via Gateway.

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

        # Get token from session state
        # Use ID token to ensure custom attributes (like allowed_agents) are available
        from services.frontend_streamlit.session import get_session_state

        state = get_session_state()
        token = state.id_token
        if not token:
            raise RuntimeError("No ID token found. Please log in.")

        try:
            config = load_config()
            base_url = config.frontend_gateway_url.rstrip("/")
            url = f"{base_url}/agents/{self.runtime_name}/invoke"

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            payload = {"message": message, "sessionId": session_id, "userId": user_id}

            logger.info(f"Invoking agent {self.runtime_name} via Gateway")

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 401:
                raise RuntimeError("Unauthorized. Please log in again.")
            if response.status_code == 403:
                raise RuntimeError(f"Access denied to agent {self.runtime_name}")
            if response.status_code == 404:
                raise RuntimeError(f"Agent {self.runtime_name} not found")

            response.raise_for_status()

            data: dict[str, Any] = response.json()
            return AgentResponse(
                session_id=data.get("sessionId", session_id),
                user_id=data.get("userId", user_id),
                message=data.get("output"),
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Gateway invocation failed: {e}")
            raise RuntimeError(f"Failed to invoke agent: {e}") from e
