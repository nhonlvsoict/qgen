from qsg.adapters.braket_qiskit import BraketQiskitAdapter
import pytest


def test_entrypoint_uses_default_context():
    adapter = BraketQiskitAdapter()
    code = adapter.entrypoint()
    assert '/app/payload/program.py' in code
    assert 'BraketLocalBackend' in code


def test_entrypoint_accepts_custom_context():
    adapter = BraketQiskitAdapter(payload_path='/tmp/foo.py')
    code = adapter.entrypoint()
    assert '/tmp/foo.py' in code
    assert '/app/payload/program.py' not in code


def test_entrypoint_missing_required_field():
    adapter = BraketQiskitAdapter(payload_path=None)
    with pytest.raises(ValueError):
        adapter.entrypoint()


def test_runtime_packages_include_dependencies():
    adapter = BraketQiskitAdapter()
    pkgs = adapter.runtime_packages()
    assert 'qiskit' in pkgs
    assert 'qiskit-braket-provider' in pkgs
    assert 'amazon-braket-sdk' in pkgs

