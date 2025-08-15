from qiskit import QuantumCircuit
from math import pi, floor, sqrt
from random import randint

def _oracle(n, marked):
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
    return oracle

def _diffuser(n):
    diff = QuantumCircuit(n)
    diff.h(range(n)); diff.x(range(n))
    diff.h(n-1); diff.mcx(list(range(n-1)), n-1); diff.h(n-1)
    diff.x(range(n)); diff.h(range(n))
    return diff

def build_circuit(n=16, marked=None):
    if marked is None:
        marked = "".join(str(randint(0,1)) for _ in range(n))
    iters = floor(pi/4 * sqrt(2**n))
    oracle = _oracle(n, marked)
    diffuser = _diffuser(n)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(iters):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)
    qc.measure(range(n), range(n))
    return qc
