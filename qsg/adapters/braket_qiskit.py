from .base import Adapter
from .template_manager import render as render_template


class BraketQiskitAdapter(Adapter):
    name = "braket-qiskit"

    def __init__(self, **kwargs):
        self.config = kwargs

    def required_ir(self) -> str:
        return "qiskit"

    def prepare_payload(self, ir_artifact) -> dict:
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["qiskit", "amazon-braket-sdk", "qiskit-braket-provider"]

    def entrypoint(self) -> str:
        context = {
            "payload_path": self.config.get("payload_path", "/app/payload/program.py"),
        }
        return render_template(
            "braket_qiskit_submit.py.j2",
            context,
            required_fields=["payload_path"],
        )

