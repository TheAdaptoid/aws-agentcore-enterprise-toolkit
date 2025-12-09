from typing import Literal, TypedDict

from services.frontend_streamlit.runtime_client_ac import AgentCoreRuntimeClient
from services.frontend_streamlit.runtime_client_base import RuntimeClient
from services.frontend_streamlit.runtime_client_local import LocalRuntimeClient

# Defines allowed runtime modalities
# Can be extended as new modalities are added
type RuntimeModality = Literal["local", "agentcore"]


class RuntimeConfig(TypedDict, total=False):
    """Configuration for runtime clients.

    Intended to contain modality specific configuration options.
    """

    base_url: str | None  # For local modality


def get_runtime_client(
    runtime_name: str,
    modality: RuntimeModality,
    config: RuntimeConfig | None = None,
) -> RuntimeClient:
    """Factory function to get the appropriate RuntimeClient.

    Args:
        runtime_name: Name of the agent/runtime
        modality: Invocation modality
        config: Optional runtime configuration

    Returns:
        An instance of RuntimeClient

    Raises:
        ValueError: If an unsupported modality is specified
        ValueError: If required config options are missing
    """
    if modality == "local":
        if config is None:
            raise ValueError("Local runtime requires a config.")
        _bu: str | None = config.get("base_url")
        if _bu is None:
            raise ValueError("Local runtime requires 'base_url' in config.")
        return LocalRuntimeClient(
            runtime_name=runtime_name,
            base_url=_bu,
        )
    elif modality == "agentcore":
        return AgentCoreRuntimeClient(runtime_name=runtime_name)
    else:
        raise ValueError(f"Unsupported runtime method: {modality}")
