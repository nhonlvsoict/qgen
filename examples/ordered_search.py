import numpy as np
from qiskit import QuantumCircuit


def build_circuit():
    # need to pass the param N and i as input for the circuit
    #  Calculate the number of qubits needed for N
    num_qubits = int(np.ceil(np.log2(N)))

    # Create a quantum circuit with N+1 qubits
    qc = QuantumCircuit(num_qubits + 1, num_qubits)

    # Initialize the search state |s⟩ = |0...01⟩
    qc.x(num_qubits)

    # Apply Hadamard gates to create a superposition of all possible states
    for i in range(num_qubits + 1):
        qc.h(i)

    # Apply the oracle to mark the target state |x⟩
    for i in range(N):
        if i == x:
            qc.cz(i, num_qubits)  # Apply a controlled-Z gate if the index matches x

    # Apply inverse quantum Fourier transform
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits + 1):
            qc.u(-2 * np.pi / 2 ** (j - i + 1), i, j, num_qubits)
        qc.h(i)

    # Measure the first num_qubits qubits
    for i in range(num_qubits):
        qc.measure(i, i)

    return qc
