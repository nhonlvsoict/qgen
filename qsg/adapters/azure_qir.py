from .base import Adapter
from . import register_adapter


@register_adapter("azure")
class AzureQIRAdapter(Adapter):
    def __init__(self, profile="base"):
        self.profile = profile

    def required_ir(self) -> str:
        return "qir"

    def prepare_payload(self, ir_artifact) -> dict:
        # In a future step, validate QIR profile and write .bc to disk
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["azure-quantum"]

    def entrypoint(self) -> str:
        # Placeholder submission
        return r"""
python - <<'PY'
print("Submitting QIR job to Azure... (stub)")
PY
"""
