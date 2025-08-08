from .base import Adapter

class BraketQasm3Adapter(Adapter):
    name = "braket"

    def required_ir(self) -> str:
        return "qasm3"

    def prepare_payload(self, ir_artifact) -> dict:
        return {"program.qasm": ir_artifact["qasm3"]}

    def runtime_packages(self) -> list[str]:
        return ["amazon-braket-sdk"]

    def entrypoint(self) -> str:
        return r"""
python - <<'PY'
print("Submitting OpenQASM 3 program to Braket... (stub)")
PY
"""
