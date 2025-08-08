from abc import ABC, abstractmethod

class Adapter(ABC):
    name: str

    @abstractmethod
    def required_ir(self) -> str:
        pass

    @abstractmethod
    def prepare_payload(self, ir_artifact) -> dict:
        pass

    @abstractmethod
    def runtime_packages(self) -> list[str]:
        pass

    @abstractmethod
    def entrypoint(self) -> str:
        pass

def load_adapter(target: str, **kwargs) -> "Adapter":
    if target == "azure":
        from .azure_qir import AzureQIRAdapter
        return AzureQIRAdapter(**kwargs)
    if target == "rigetti":
        from .rigetti_qir import RigettiQIRAdapter
        return RigettiQIRAdapter(**kwargs)
    if target == "ibm":
        from .ibm_qasm3 import IBMQasm3Adapter
        return IBMQasm3Adapter(**kwargs)
    if target == "braket":
        from .braket_qasm3 import BraketQasm3Adapter
        return BraketQasm3Adapter(**kwargs)
    raise ValueError(f"Unknown target: {target}")
