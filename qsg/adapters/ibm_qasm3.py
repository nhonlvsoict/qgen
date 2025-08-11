from pathlib import Path
from jinja2 import Template

from .base import Adapter

class IBMQasm3Adapter(Adapter):
    name = "ibm"

    def __init__(self, **kwargs):
        # Store kwargs if needed, or just accept them to avoid errors
        self.config = kwargs

    def required_ir(self) -> str:
        return "qasm3"

    def prepare_payload(self, ir_artifact) -> dict:
        qasm3 = ir_artifact["qasm3"]
        return {"program.qasm": qasm3}

    def runtime_packages(self) -> list[str]:
        return ["qiskit", "qiskit-ibm-runtime", "qiskit_qasm3_import", "qiskit-aer"]

    def entrypoint(self) -> str:
        """Render the IBM Sampler wrapper with context."""
        template_path = Path(__file__).parent / "templates" / "ibm_sampler.py.j2"
        template_text = template_path.read_text()
        context = {
            "payload_path": self.config.get("payload_path", "/app/payload/program.qasm"),
            "token_env": self.config.get("token_env", "IBM_TOKEN"),
        }
        return Template(template_text).render(context)
