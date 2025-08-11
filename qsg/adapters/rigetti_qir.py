from .base import Adapter
from . import register_adapter


@register_adapter("rigetti")
class RigettiQIRAdapter(Adapter):

    def __init__(self, **kwargs):
        # Store kwargs if needed, or just accept them to avoid errors
        self.config = kwargs

    def required_ir(self) -> str:
        return "qir"

    def prepare_payload(self, ir_artifact) -> dict:
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["qcs-sdk-python"]

    def entrypoint(self) -> str:
        return r"""
python - <<'PY'
print("Submitting QIR->Quil job to Rigetti... (stub)")
PY
"""
