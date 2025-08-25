import pytest

from qsg.adapters.braket_qasm3 import BraketQasm3Adapter


def test_entrypoint_uses_default_context():
    adapter = BraketQasm3Adapter(device_arn="arn:aws:braket:::device/qpu/test", region="us-west-2")
    code = adapter.entrypoint()
    assert '/app/payload/program.qasm' in code
    assert 'arn:aws:braket:::device/qpu/test' in code
    assert 'us-west-2' in code
    assert 'shots=1000' in code


def test_entrypoint_accepts_custom_context():
    adapter = BraketQasm3Adapter(
        payload_path='/tmp/foo.qasm',
        device_arn='arn:aws:braket:::device/qpu/foo',
        region='eu-west-1',
        shots=200,
    )
    code = adapter.entrypoint()
    assert '/tmp/foo.qasm' in code
    assert 'arn:aws:braket:::device/qpu/foo' in code
    assert 'eu-west-1' in code
    assert 'shots=200' in code
    assert '/app/payload/program.qasm' not in code


def test_entrypoint_missing_required_field():
    adapter = BraketQasm3Adapter(device_arn='arn:aws:braket:::device/qpu/test')
    with pytest.raises(ValueError):
        adapter.entrypoint()


def test_runtime_packages():
    adapter = BraketQasm3Adapter()
    assert 'amazon-braket-sdk' in adapter.runtime_packages()
