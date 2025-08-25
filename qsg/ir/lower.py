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
        return {"program.qasm": dumps(qc)}

    elif kind == "qir":
        if src.suffix in {".bc", ".ll"}:
            # Pass-through for pre-generated QIR bitcode or textual LLVM IR
            return {f"program{src.suffix}": src.read_bytes()}

        if src.suffix == ".py":
            from qiskit import QuantumCircuit
            from qiskit_qir import to_qir_module

            scope = {}
            exec(src.read_text(), scope)
            if "build_circuit" not in scope:
                raise ValueError("Expected a build_circuit() function in the source file.")
            qc = scope["build_circuit"]()
            if not isinstance(qc, QuantumCircuit):
                raise TypeError("build_circuit() must return a qiskit.QuantumCircuit.")
            module, _ = to_qir_module(qc)
            return {"program.ll": str(module).encode()}

        raise ValueError("QIR input must be a .py, .bc, or .ll file")
    else:
        raise ValueError(f"Unknown IR kind: {kind}")
