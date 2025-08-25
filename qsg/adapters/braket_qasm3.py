from .base import Adapter
from .template_manager import render as render_template


class BraketQasm3Adapter(Adapter):
    name = "braket"

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
        context = {
            "payload_path": self.config.get("payload_path", "/app/payload/program.qasm"),
            "shots": self.config.get("shots", 8192),
        }
        return render_template(
            "braket_submit.py.j2",
            context,
            required_fields=["payload_path", "device_arn", "region"],
        )
