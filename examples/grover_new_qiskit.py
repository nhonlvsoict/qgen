import os
from math import pi, floor, sqrt

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def oracle_with_ancilla(n, marked):
    # n data qubits + 1 ancilla
    qc = QuantumCircuit(n+1, name="O")
    anc = n
    # prepare ancilla in |-> for phase kickback
    qc.x(anc); qc.h(anc)

    # turn the marked string into the all-ones condition
    for i, b in enumerate(marked):
        if b == "0":
            qc.x(i)

    # one multi-controlled X onto the ancilla
    qc.mcx(list(range(n)), anc)

    # undo the X masking
    for i, b in enumerate(marked):
        if b == "0":
            qc.x(i)

    # unprepare ancilla
    qc.h(anc); qc.x(anc)
    return qc

def diffuser_with_ancilla(n):
    qc = QuantumCircuit(n+1, name="D")
    anc = n
    qc.h(range(n)); qc.x(range(n))

    # same phase-kickback trick to implement multi-controlled Z
    qc.x(anc); qc.h(anc)
    qc.mcx(list(range(n)), anc)
    qc.h(anc); qc.x(anc)

    qc.x(range(n)); qc.h(range(n))
    return qc

def build_circuit(n=None, marked=None):
    if n is None:
        n = int(os.getenv("QGEN_N", "4"))
     
        print(f"Using n={n} from environment variable QGEN_N")
    if marked is None:
        default = "0"*(n-1) + "1"
        marked = os.getenv("QGEN_MARKED", default)[:n]
        print(f"Using marked={marked} from environment variable QGEN_MARKED")
    if iters is None:
        iters = max(1, min(2, floor(pi/4 * sqrt(2**n))))  # hardware-friendly
    qc = QuantumCircuit(n+1, n)  # +1 ancilla
    qc.h(range(n))
    O = oracle_with_ancilla(n, marked)
    D = diffuser_with_ancilla(n)
    for _ in range(iters):
        qc.compose(O, inplace=True)
        qc.compose(D, inplace=True)
    # measure only the data qubits
    qc.measure(range(n), range(n))
    return qc