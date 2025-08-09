# Quantum Service Generator (QSG)

Vendor-neutral quantum service generator. Input: Python quantum code.
Outputs: provider-ready payload (QASM 3 or QIR) baked into an OCI image
you can run locally or on Kubernetes.
Current supported providers:
- IBM (QASM 3)
- Azure
- Rigetti
- Braket.
