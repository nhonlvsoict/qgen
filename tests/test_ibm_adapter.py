from qsg.adapters.ibm_qasm3 import IBMQasm3Adapter
import pytest


def test_entrypoint_uses_default_context():
    adapter = IBMQasm3Adapter()
    code = adapter.entrypoint()
    assert '/app/payload/program.qasm' in code
    assert 'os.getenv("IBM_TOKEN")' in code
    assert 'No IBM_TOKEN env var found' in code


def test_entrypoint_accepts_custom_context():
    adapter = IBMQasm3Adapter(payload_path='/tmp/foo.qasm', token_env_var='MY_TOKEN')
    code = adapter.entrypoint()
    assert '/tmp/foo.qasm' in code
    assert 'os.getenv("MY_TOKEN")' in code
    assert 'No MY_TOKEN env var found' in code
    assert '/app/payload/program.qasm' not in code
    assert 'IBM_TOKEN' not in code


def test_entrypoint_missing_required_field():
    adapter = IBMQasm3Adapter(token_env_var=None)
    with pytest.raises(ValueError):
        adapter.entrypoint()
