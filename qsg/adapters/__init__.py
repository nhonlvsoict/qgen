"""Adapter registration and loading utilities."""

from .base import Adapter, load_adapter, register_adapter

# Import built-in adapters so they register themselves via the decorator.
from . import azure_qir  # noqa: F401
from . import braket_qasm3  # noqa: F401
from . import ibm_qasm3  # noqa: F401
from . import rigetti_qir  # noqa: F401

__all__ = ["Adapter", "load_adapter", "register_adapter"]
