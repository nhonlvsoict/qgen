from .base import Adapter
from .template_manager import render as render_template


class GoogleCirqAdapter(Adapter):
    name = "google"

    def __init__(self, **kwargs):
        # Store kwargs if needed, or just accept them to avoid errors
        self.config = kwargs

    def required_ir(self) -> str:
        return "qasm3"

    def prepare_payload(self, ir_artifact) -> dict:
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["cirq", "cirq-google"]

    def entrypoint(self) -> str:
        context = {
            "payload_path": self.config.get("payload_path", "/app/payload/program.qasm"),
            "project_id_env_var": self.config.get("project_id_env_var", "GOOGLE_PROJECT_ID"),
        }
        return render_template(
            "google_submit.py.j2",
            context,
            required_fields=["payload_path", "project_id_env_var"],
        )
