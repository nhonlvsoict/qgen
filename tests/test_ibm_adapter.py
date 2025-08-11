from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from qsg.adapters.ibm_qasm3 import IBMQasm3Adapter


def test_entrypoint_default_context():
    adapter = IBMQasm3Adapter()
    entry = adapter.entrypoint()
    assert "/app/payload/program.qasm" in entry
    assert "IBM_TOKEN" in entry


def test_entrypoint_custom_context():
    adapter = IBMQasm3Adapter(payload_path="/tmp/foo.qasm", token_env="QISKIT_TOKEN")
    entry = adapter.entrypoint()
    assert "/tmp/foo.qasm" in entry
    assert "QISKIT_TOKEN" in entry
    assert "/app/payload/program.qasm" not in entry
    assert "IBM_TOKEN" not in entry
