from .base import Adapter
from .template_manager import render as render_template
from . import register_adapter


@register_adapter("ibm")
class IBMQasm3Adapter(Adapter):

    def __init__(self, **kwargs):
        # Store kwargs if needed, or just accept them to avoid errors
        self.config = kwargs

    def required_ir(self) -> str:
        return "qasm3"

    def prepare_payload(self, ir_artifact) -> dict:
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["qiskit", "qiskit-ibm-runtime", "qiskit_qasm3_import", "qiskit-aer"]

    def entrypoint(self) -> str:
        context = {
            "payload_path": self.config.get("payload_path", "/app/payload/program.qasm"),
            "token_env_var": self.config.get("token_env_var", "IBM_TOKEN"),
        }
        return render_template(
            "ibm_sampler.py.j2",
            context,
            required_fields=["payload_path", "token_env_var"],
        )
