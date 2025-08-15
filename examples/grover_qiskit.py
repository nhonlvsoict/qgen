from qiskit import QuantumCircuit
from math import pi, floor, sqrt
from random import randint

def build_circuit(n=4, marked=None):
    if marked is None:
        marked = "".join(str(randint(0,1)) for _ in range(n))
    print(f"[INFO] Grover experiment — n={n}, marked={marked}")

    # Oracle for single marked state
    oracle = QuantumCircuit(n)
    for i, bit in enumerate(marked):
        if bit == "0":
            oracle.x(i)
    oracle.h(n-1)
    oracle.mcx(list(range(n-1)), n-1)
    oracle.h(n-1)
    for i, bit in enumerate(marked):
        if bit == "0":
            oracle.x(i)

    # Diffusion
    diffuser = QuantumCircuit(n)
    diffuser.h(range(n))
    diffuser.x(range(n))
    diffuser.h(n-1)
    diffuser.mcx(list(range(n-1)), n-1)
    diffuser.h(n-1)
    diffuser.x(range(n))
    diffuser.h(range(n))

    # Grover iteration count
    iterations = floor(pi/4 * sqrt(2**n))
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)
    qc.measure(range(n), range(n))
    return qc
