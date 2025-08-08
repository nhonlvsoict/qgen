from .base import Adapter

class RigettiQIRAdapter(Adapter):
    name = "rigetti"

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
