from .base import Adapter

class IBMQasm3Adapter(Adapter):
    name = "ibm"

    def required_ir(self) -> str:
        return "qasm3"

    def prepare_payload(self, ir_artifact) -> dict:
        qasm3 = ir_artifact["qasm3"]
        return {"program.qasm": qasm3}

    def runtime_packages(self) -> list[str]:
        return ["qiskit", "qiskit-ibm-runtime"]

    def entrypoint(self) -> str:
        # Uses IBM Token via env var IBM_TOKEN; runs a quick Sampler job
        return r"""
python - <<'PY'
import os
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit.qasm3 import loads

qasm3 = open("/app/payload/program.qasm").read()
qc = loads(qasm3)

token = os.getenv("IBM_TOKEN")
if not token:
    print("No IBM_TOKEN env var found; running local simulation via qiskit instead.")
    from qiskit.primitives import Sampler as LocalSampler
    sampler = LocalSampler()
    print(sampler.run(qc).result())
else:
    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    sampler = Sampler(session=None)
    print(sampler.run(qc).result())
PY
"""
