from qsg.adapters import Adapter, load_adapter, register_adapter, ADAPTER_REGISTRY


@register_adapter("dummy")
class DummyAdapter(Adapter):
    def required_ir(self) -> str:
        return "dummy"

    def prepare_payload(self, ir_artifact) -> dict:
        return ir_artifact

    def runtime_packages(self) -> list[str]:
        return []

    def entrypoint(self) -> str:
        return "echo dummy"


def test_dynamic_registry_allows_new_adapters():
    # ensure adapter can be loaded via the registry
    adapter = load_adapter("dummy")
    assert isinstance(adapter, DummyAdapter)

    # cleanup to avoid leaking test adapter to other tests
    ADAPTER_REGISTRY.pop("dummy", None)
