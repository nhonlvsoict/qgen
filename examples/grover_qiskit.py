import os
from qiskit import QuantumCircuit
from math import pi, floor, sqrt

def _oracle(n, marked):
    oracle = QuantumCircuit(n)
    for i, bit in enumerate(marked):
        if bit == "0":
            oracle.x(i)
    oracle.h(n-1); oracle.mcx(list(range(n-1)), n-1); oracle.h(n-1)
    for i, bit in enumerate(marked):
        if bit == "0":
            oracle.x(i)
    return oracle

def _diffuser(n):
    diff = QuantumCircuit(n)
    diff.h(range(n)); diff.x(range(n))
    diff.h(n-1); diff.mcx(list(range(n-1)), n-1); diff.h(n-1)
    diff.x(range(n)); diff.h(range(n))
    return diff

def build_circuit(n=None, marked=None):
    if n is None:
        n = int(os.getenv("QGEN_N", "4"))
     
        print(f"Using n={n} from environment variable QGEN_N")
    if marked is None:
        default = "0"*(n-1) + "1"
        marked = os.getenv("QGEN_MARKED", default)[:n]
        print(f"Using marked={marked} from environment variable QGEN_MARKED")
    # iters = floor(pi/4 * sqrt(2**n))
    iters = max(1, min(2, floor(pi/4 * sqrt(2**n))))  # clamp to 1..2 for hardware
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    oracle = _oracle(n, marked)
    diffuser = _diffuser(n)
    for _ in range(iters):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)
    qc.measure(range(n), range(n))
    return qc