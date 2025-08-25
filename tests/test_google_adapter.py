from qsg.adapters import load_adapter
from qsg.adapters.google_cirq import GoogleCirqAdapter
import pytest


def test_adapter_loading():
    adapter = load_adapter("google")
    assert isinstance(adapter, GoogleCirqAdapter)


def test_entrypoint_uses_default_context():
    adapter = GoogleCirqAdapter()
    code = adapter.entrypoint()
    assert '/app/payload/program.qasm' in code
    assert 'os.getenv("GOOGLE_PROJECT_ID")' in code
    assert 'No GOOGLE_PROJECT_ID env var found' in code


def test_entrypoint_accepts_custom_context():
    adapter = GoogleCirqAdapter(payload_path='/tmp/foo.qasm', project_id_env_var='MY_GOOGLE_PROJECT')
    code = adapter.entrypoint()
    assert '/tmp/foo.qasm' in code
    assert 'os.getenv("MY_GOOGLE_PROJECT")' in code
    assert 'No MY_GOOGLE_PROJECT env var found' in code
    assert '/app/payload/program.qasm' not in code
    assert 'GOOGLE_PROJECT_ID' not in code


def test_entrypoint_missing_required_field():
    adapter = GoogleCirqAdapter(project_id_env_var=None)
    with pytest.raises(ValueError):
        adapter.entrypoint()


def test_runtime_packages():
    adapter = GoogleCirqAdapter()
    packages = adapter.runtime_packages()
    assert 'cirq' in packages
    assert 'cirq-google' in packages
