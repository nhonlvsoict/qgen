from abc import ABC, abstractmethod
from typing import Dict, Type


ADAPTER_REGISTRY: Dict[str, Type["Adapter"]] = {}


def register_adapter(name: str):
    """Class decorator to register an adapter implementation."""

    def _decorator(cls: Type["Adapter"]):
        ADAPTER_REGISTRY[name] = cls
        return cls

    return _decorator


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
    """Instantiate a registered adapter for ``target``.

    Adapters register themselves via :func:`register_adapter`.
    """

    try:
        adapter_cls = ADAPTER_REGISTRY[target]
    except KeyError as exc:
        raise ValueError(f"Unknown target: {target}") from exc
    return adapter_cls(**kwargs)
