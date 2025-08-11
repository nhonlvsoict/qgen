# QGen Architecture

QGen (Quantum Generation Toolkit) turns user quantum circuits into provider-ready services.
This document outlines the proposed design based on the latest planning discussion.

## 1. Overall Architecture and Components

### a. Input Interface and Configuration Manager
- **User Code Input**: Accept quantum circuit code written in different languages (e.g., Python for Qiskit, Q#, Cirq).
- **Configuration File**: Users specify target provider(s) (IBM, Google, Amazon, Microsoft) and desired execution mode (fresh submission or session reuse).
- **Language & Provider Detection**: Next iteration (MVP2) should auto-detect the programming language and map it to the correct provider template.

### b. Template Repository and Code Generation Engine
- **Wrapper Templates**: Maintain Jinja2 templates for each language-provider combination, such as:
  - Qiskit–IBM template wrapping a circuit into a Qiskit Runtime job (see `qsg/adapters/templates/ibm_sampler.py.j2`).
  - Cirq–Google template that handles mapping and transpilation for Quantum Engine.
  - Q#–Azure Quantum template for job submission.
- **IR Transpilation Module**: Transpile quantum code into IR (QIR or OpenQASM 3) for portability.
- **Code Generation Module**: Inject boilerplate code (authentication, transpilation, API formatting) into the user’s code without introducing a new meta‑language.
- **Runtime Interface**: Sends the containerized quantum circuit to the provider’s execution endpoint. Support re-submission as a job or session reuse (“deploy once, call many times”).

### c. Containerization and Packaging Module
- **Container Tool Integration**: Use containerization frameworks (Docker Buildpacks, Jib for Java) to package generated code and dependencies into images.
- **Image Optimization**: Employ layered builds and caching to reduce image size and startup time.

## 2. Additional Considerations
- **Modularity and Extensibility**: The design must allow new templates and provider APIs to be added easily as hardware evolves.
- **Error Handling and Validation**: Perform static analysis (inspired by the FRANC framework) to validate generated code against provider requirements before submission.
- **Performance Optimization**: Integrate session-based or pre‑deployed execution modes to reduce latency. Otherwise, optimize container startup and submission routines.
- **Security**: Manage API tokens and credentials securely through environment variables or secret stores within container environments.

