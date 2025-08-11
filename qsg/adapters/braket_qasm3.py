from .base import Adapter
from . import register_adapter


@register_adapter("braket")
class BraketQasm3Adapter(Adapter):

    def __init__(self, **kwargs):
        # Store kwargs if needed, or just accept them to avoid errors
        self.config = kwargs

    def required_ir(self) -> str:
        return "qasm3"

    def prepare_payload(self, ir_artifact) -> dict:
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["amazon-braket-sdk"]

    def entrypoint(self) -> str:
        return r"""
python - <<'PY'
print("Submitting OpenQASM 3 program to Braket... (stub)")
PY
"""
