from qsg.adapters import Adapter, load_adapter, register_adapter


def test_load_existing_adapter():
    adapter = load_adapter("ibm")
    from qsg.adapters.ibm_qasm3 import IBMQasm3Adapter
    assert isinstance(adapter, IBMQasm3Adapter)


def test_register_new_adapter():
    @register_adapter("dummy")
    class DummyAdapter(Adapter):
        def required_ir(self) -> str:
            return "noop"

        def prepare_payload(self, ir_artifact) -> dict:
            return {}

        def runtime_packages(self) -> list[str]:
            return []

        def entrypoint(self) -> str:
            return ""

    adapter = load_adapter("dummy")
    assert isinstance(adapter, DummyAdapter)
