from pathlib import Path

def lower_to_ir(src_path: str, kind: str):
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(src_path)

    if kind == "qasm3":
        from qiskit.qasm3 import dumps
        from qiskit import QuantumCircuit

        scope = {}
        exec(src.read_text(), scope)
        if "build_circuit" not in scope:
            raise ValueError("Expected a build_circuit() function in the source file.")
        qc = scope["build_circuit"]()
        if not isinstance(qc, QuantumCircuit):
            raise TypeError("build_circuit() must return a qiskit.QuantumCircuit.")
        return {"qasm3": dumps(qc)}

    elif kind == "qir":
        # Placeholder for PyQIR/pytket-qir integration
        raise NotImplementedError("QIR path not wired yet.")
    else:
        raise ValueError(f"Unknown IR kind: {kind}")
