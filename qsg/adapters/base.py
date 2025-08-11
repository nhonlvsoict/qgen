from abc import ABC, abstractmethod

from . import ADAPTER_REGISTRY


class Adapter(ABC):
    name: str

    @abstractmethod
    def required_ir(self) -> str:
        pass

    @abstractmethod
    def prepare_payload(self, ir_artifact) -> dict:
        pass

    @abstractmethod
    def runtime_packages(self) -> list[str]:
        pass

    @abstractmethod
    def entrypoint(self) -> str:
        pass


def load_adapter(target: str, **kwargs) -> "Adapter":
    """Instantiate an adapter for ``target`` using the registration registry."""

    # print all ADAPTER_REGISTRY here for debugging purposes
    print("ADAPTER_REGISTRY:", ADAPTER_REGISTRY)

    try:
        adapter_cls = ADAPTER_REGISTRY[target]
    except KeyError as exc:  # pragma: no cover - error path
        raise ValueError(f"Unknown target: {target}") from exc
    return adapter_cls(**kwargs)
