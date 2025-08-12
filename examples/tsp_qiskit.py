from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from numpy import pi

def build_circuit():
    qreg_q = QuantumRegister(5, 'q')
    creg_c = ClassicalRegister(5, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.h(qreg_q[0])
    circuit.x(qreg_q[1])
    circuit.x(qreg_q[2])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    circuit.cx(qreg_q[1], qreg_q[0])
    circuit.cx(qreg_q[2], qreg_q[0])
    circuit.barrier(qreg_q[0], qreg_q[1], qreg_q[2])
    circuit.h(qreg_q[0])
    circuit.measure(qreg_q[0], creg_c[0])
    circuit.measure(qreg_q[1], creg_c[1])
    circuit.measure(qreg_q[2], creg_c[2])
    return circuit
