"""Adapter registration utilities.

This module exposes a simple registry mapping provider names to adapter
implementations. Adapters can register themselves via the ``register_adapter``
decorator. The :func:`qsg.adapters.base.load_adapter` function performs dynamic
lookups against this registry.
"""

from __future__ import annotations

from typing import Callable, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from .base import Adapter


ADAPTER_REGISTRY: Dict[str, Type["Adapter"]] = {}


def register_adapter(name: str) -> Callable[[Type["Adapter"]], Type["Adapter"]]:
    """Class decorator used by adapters to self-register.

    Parameters
    ----------
    name:
        Provider name used to load the adapter.
    """

    def decorator(cls: Type["Adapter"]) -> Type["Adapter"]:
        ADAPTER_REGISTRY[name] = cls
        cls.name = name
        return cls

    return decorator


from .base import Adapter, load_adapter

__all__ = ["Adapter", "load_adapter", "register_adapter", "ADAPTER_REGISTRY"]

