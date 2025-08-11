import sys
import types
import pytest
from qsg.ir.lower import lower_to_ir


def test_lower_to_ir_qasm3(tmp_path):
    qiskit = types.ModuleType('qiskit')
    class QuantumCircuit:
        def __init__(self, n):
            self.n = n
        def x(self, q):
            pass
    qiskit.QuantumCircuit = QuantumCircuit
    qasm3_mod = types.ModuleType('qiskit.qasm3')
    qasm3_mod.dumps = lambda qc: 'OPENQASM 3;'
    qiskit.qasm3 = qasm3_mod
    sys.modules['qiskit'] = qiskit
    sys.modules['qiskit.qasm3'] = qasm3_mod

    src = tmp_path / 'circuit.py'
    src.write_text(
        'from qiskit import QuantumCircuit\n'
        'def build_circuit():\n'
        '    qc = QuantumCircuit(1)\n'
        '    qc.x(0)\n'
        '    return qc\n'
    )
    result = lower_to_ir(str(src), 'qasm3')
    assert 'program.qasm' in result
    assert 'OPENQASM 3;' in result['program.qasm']


def test_lower_to_ir_qir(tmp_path):
    src = tmp_path / 'program.bc'
    src.write_bytes(b'1234')
    result = lower_to_ir(str(src), 'qir')
    assert result == {'program.bc': b'1234'}


def test_lower_to_ir_unknown(tmp_path):
    src = tmp_path / 'program.txt'
    src.write_text('hello')
    with pytest.raises(ValueError):
        lower_to_ir(str(src), 'unknown')
