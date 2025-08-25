from .base import Adapter
from .template_manager import render as render_template

class AzureQIRAdapter(Adapter):
    name = "azure"

    def __init__(self, profile="base", **kwargs):
        self.profile = profile
        self.config = kwargs

    def required_ir(self) -> str:
        return "qir"

    def prepare_payload(self, ir_artifact) -> dict:
        # In a future step, validate QIR profile and write .bc to disk
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return ["azure-quantum", "azure-identity"]

    def entrypoint(self) -> str:
        context = {
            "payload_path": self.config.get("payload_path", "/app/payload/program.bc"),
            "target": self.config.get("target", "quantinuum.sim.h1-1sc"),
        }
        return render_template(
            "azure_submit.py.j2",
            context,
            required_fields=["payload_path", "target"],
        )
