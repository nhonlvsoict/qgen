from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from numpy import pi
import os, json, time
from datetime import datetime

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.qasm3 import loads

import itertools
import numpy as np

# -----------------------------
# 1. Định nghĩa instance con
# -----------------------------
N_SYS = 3  # số antenna / qubit hệ thống

# Tham số J, A 
J = {
    (0, 1): 0.8,
    (1, 2): 0.5,
}
A = {
    0: -0.3,
    1:  0.1,
    2:  0.2,
}

def bitstring_to_z(bits):
    """
    Map bitstring '010' -> z_i in {+1, -1}
    Chọn |0> -> z=+1, |1> -> z=-1
    """
    return [1 if b == '0' else -1 for b in bits]

def energy_H(bits):
    """H(z) cho bitstring bits (str) theo Hamiltonian gốc."""
    z = bitstring_to_z(bits)
    # term ZZ
    e = 0.0
    for (i, j), Jij in J.items():
        e += Jij * z[i] * z[j]
    # term Z
    for i, Ai in A.items():
        e += Ai * z[i]
    return e

# Liệt kê tất cả cấu hình để tìm E_min, E_max và ground state
all_bits = [''.join(bs) for bs in itertools.product('01', repeat=N_SYS)]
energies = {bits: energy_H(bits) for bits in all_bits}
E_min = min(energies.values())
E_max = max(energies.values())

# tìm ground state
z_gs_bits = min(energies, key=energies.get)
E_gs = energies[z_gs_bits]
print("Ground state bitstring:", z_gs_bits, "E_min =", E_gs)

# -----------------------------
# 2. Scale Hamiltonian để đưa vào QPE
# -----------------------------
E_range = E_max - E_min

def scaled_coeffs():
    """
    Tính hệ số h_ZZ, h_Z cho Hamiltonian đã scale,
    bỏ constant shift (global phase).
    """
    # Với H'(z) = (H(z) - E_min) / E_range
    # Ta viết H' = const + sum h_ij z_i z_j + sum h_i z_i
    h_zz = {}
    h_z = {}

    # Chú ý: vì scaling là affine H' = (H - E_min)/E_range,
    # phần linear / quadratic đều chia cho E_range,
    # constant shift = -E_min/E_range ta bỏ qua.
    for (i, j), Jij in J.items():
        h_zz[(i, j)] = Jij / E_range
    for i, Ai in A.items():
        h_z[i] = Ai / E_range

    return h_zz, h_z

h_zz, h_z = scaled_coeffs()


def time_evolution_gate(t, n_sys, h_zz, h_z):
    """
    Xây gate U(t) = exp(i t H'), với H' = sum h_zz Z_i Z_j + sum h_z Z_i.
    """
    qr = QuantumRegister(n_sys, 'sys')
    qc = QuantumCircuit(qr, name=f"U({t:.2f})")

    # term ZZ
    for (i, j), coeff in h_zz.items():
        theta = 2 * t * coeff * 2 * np.pi  # factor 2pi để eigenphase ∈ [0,1)
        # e^{i t coeff Z_i Z_j} ~ RZZ(theta)
        qc.rzz(theta, qr[i], qr[j])

    # term Z
    for i, coeff in h_z.items():
        theta = 2 * t * coeff * 2 * np.pi
        qc.rz(theta, qr[i])

    return qc.to_gate()

def apply_controlled_time_evolution(qc, ctrl_qubit, sys_qubits, t, h_zz, h_z):
    """
    Thêm controlled-U(t) với ctrl_qubit là control,
    U(t) acting trên sys_qubits.
    """
    U = time_evolution_gate(t, len(sys_qubits), h_zz, h_z)
    cU = U.control(1)
    qc.append(cU, [ctrl_qubit] + list(sys_qubits))


def build_circuit(t_anc=3):
    """
    Xây mạch QPE cho ground state đã biết (z_gs_bits).
    t_anc: số qubit phase (độ chính xác pha).
    """
    phase = QuantumRegister(t_anc, 'phase')
    sys = QuantumRegister(N_SYS, 'sys')
    c_phase = ClassicalRegister(t_anc, 'c_phase')

    qc = QuantumCircuit(phase, sys, c_phase)

    # 1) Chuẩn bị trạng thái hệ thống = |z_gs>
    # mapping: bit '1' -> |1>, '0' -> |0>
    for i, b in enumerate(z_gs_bits):
        if b == '1':
            qc.x(sys[i])

    # 2) Hadamard trên phase qubits
    qc.h(phase)

    # 3) Controlled-U^{2^k}
    # ở đây dùng t = 1 cho U, và power = 2^k absorb vào t_effective
    for k in range(t_anc):
        power = 2**k
        t_effective = power  # có thể scale thêm nếu muốn
        apply_controlled_time_evolution(
            qc, phase[k], sys, t_effective, h_zz, h_z
        )

    # 4) Inverse QFT trên phase register
    iqft = QFT(num_qubits=t_anc, inverse=True, do_swaps=True).to_gate(label="IQFT")
    qc.append(iqft, phase)

    # 5) Đo phase
    qc.measure(phase, c_phase)

    return qc

def extract_counts_v2(primitive_result):
    """Get counts dict from Primitives v2 Sampler result."""
    try:
        pub = primitive_result[0]  # SamplerPubResult
        return pub.join_data().get_counts()
    except Exception:
        try:
            return pub.data.c.get_counts()  # common reg name
        except Exception:
            return None

start = time.time()
qc = build_circuit()

token = os.getenv("IBM_TOKEN")
result_payload = {"backend_mode": None, "counts": None, "elapsed_s": None}

if not token:
    # Local simulation
    # If the token is not set, we will run a local simulation using Qiskit
    # This is useful for testing or when the IBM Quantum Experience is not available
    print("No IBM_TOKEN env var found; running local simulation via qiskit instead.")
    # try:
    #     from qiskit_aer.primitives import Sampler as LocalSampler
    # except ImportError:
    #     from qiskit_ibm_runtime import Sampler as LocalSampler
    from qiskit_aer.primitives import Sampler

    sampler = Sampler(run_options={"shots": 4096})
    res = sampler.run(qc).result()

    # samples = res[0].data["samples"]
    result_payload["backend_mode"] = "aer_local"
    # For primitives v0, use quasi_dists; newer APIs may have .quasi_dists or ._pub_results
    # qd = getattr(res, "quasi_dists", None)
    result_payload["counts"] = res.get_counts()
else:
    #ibm_quantum_platform
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="quantum")
    #backend = service.least_busy(operational=True, simulator=False)
    
    # Specify the backend by name
    backend = service.backend("ibm_torino")

    sampler = Sampler(mode=backend)
    sampler.options.default_shots = 4000  # Options can be set using auto-complete.

    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    isa_circuit = pm.run(qc)
    job = sampler.run([isa_circuit])
    
    # Get job properties
    props = job.properties()

    res = job.result()
    result_payload["backend_mode"] = "ibmq_qasm"
    # result_payload["properties"] = props_to_dict(props, res)
    result_payload["counts"] = extract_counts_v2(res)



result_payload["elapsed_s"] = round(time.time() - start, 4)
print(json.dumps(result_payload))
