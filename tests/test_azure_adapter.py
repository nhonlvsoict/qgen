from qsg.adapters.azure_qir import AzureQIRAdapter
import pytest


def test_entrypoint_uses_default_context():
    adapter = AzureQIRAdapter()
    code = adapter.entrypoint()
    assert '/app/payload/program.ll' in code
    assert 'rigetti.sim.qvm' in code
    # ensure authentication env vars are referenced
    assert 'CONNECTION_STRING' in code


def test_entrypoint_accepts_custom_context():
    adapter = AzureQIRAdapter(payload_path='/tmp/foo.bc', target='quantinuum.qpu')
    code = adapter.entrypoint()
    assert '/tmp/foo.bc' in code
    assert 'quantinuum.qpu' in code
    assert '/app/payload/program.ll' not in code
    assert 'rigetti.sim.qvm' not in code


def test_entrypoint_missing_required_field():
    adapter = AzureQIRAdapter(target=None)
    with pytest.raises(ValueError):
        adapter.entrypoint()


def test_runtime_packages_include_dependencies():
    adapter = AzureQIRAdapter()
    pkgs = adapter.runtime_packages()
    assert 'azure-quantum' in pkgs
    assert 'azure-identity' in pkgs

