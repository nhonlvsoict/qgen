#Edward Farhi, Jeffrey Goldstone, Sam Gutmann, and Michael Sipser Invariant quantum algorithms for insertion into an ordered list. arXiv:quant-ph/9901059, 1999.
# The Ordered Search algorithm is a quantum algorithm designed to search for a specific number in a sorted list with a significant speedup compared to classical binary search.

import numpy as np
from qiskit import QuantumCircuit, transpile
# from qiskit.compiler  import assemble
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

def ordered_search_circuit(N, x):
    # Calculate the number of qubits needed for N
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

# Define the parameters
N = 5  # Size of the sorted list
x = 2   # Number to search for

# Create the quantum circuit for the Ordered Search
search_circuit = ordered_search_circuit(N, x)

# Simulate the circuit
simulator = Aer.get_backend('qasm_simulator')
compiled_circuit = transpile(search_circuit, simulator)
# job = assemble(compiled_circuit, shots=1024)
result = simulator.run(job).result()

# Display the measurement results
counts = result.get_counts(search_circuit)
print(counts)
plot_histogram(counts)