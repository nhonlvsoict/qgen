# import Aer here, before calling qiskit_ionq_provider
from qiskit_aer import Aer
from qiskit_ionq import IonQProvider 
from qiskit import QuantumCircuit
from qiskit.providers.jobstatus import JobStatus

# Call provider and set token value
provider = IonQProvider()


# Create a bell state circuit.
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Get an IonQ simulator backend to run circuits on:
backend = provider.get_backend("ionq_simulator")

# Then run the circuit:
job = backend.run(qc, shots=1000)

# Save job_id
job_id_bell = job.job_id()

# Fetch the result:
result = job.result()


print(result.get_counts())
