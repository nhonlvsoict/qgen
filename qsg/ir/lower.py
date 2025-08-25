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
            import qiskit
            QuantumCircuit = qiskit.QuantumCircuit
            transpile = getattr(qiskit, "transpile", lambda qc, basis_gates, optimization_level: qc)
            from qiskit_qir import to_qir_module

            scope = {}
            exec(src.read_text(), scope)
            if "build_circuit" not in scope:
                raise ValueError("Expected a build_circuit() function in the source file.")

            qc = scope["build_circuit"]()
            if not isinstance(qc, QuantumCircuit):
                raise TypeError("build_circuit() must return a qiskit.QuantumCircuit.")
            ALLOWED = ['rx','ry','rz','x','y','z','h','s','sdg','t','tdg',
           'cx','cz','ccx','swap','id','measure','reset','delay','barrier']

            qc = transpile(qc, basis_gates=ALLOWED, optimization_level=1)
            module, _ = to_qir_module(qc)
            return {"program.ll": str(module).encode()}

        raise ValueError("QIR input must be a .py, .bc, or .ll file")
    elif kind == "qiskit":
        if src.suffix != ".py":
            raise ValueError("Qiskit input must be a .py file")
        return {"program.py": src.read_text()}
    else:
        raise ValueError(f"Unknown IR kind: {kind}")
