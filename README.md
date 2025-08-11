# QGen Toolkit

QGen is a vendor‑neutral toolkit that turns quantum programs into provider-ready services.
It accepts quantum circuit code in multiple languages (e.g., Qiskit, Cirq, Q#) and packages
it with provider boilerplate into a container image ready for deployment on systems like
Kubernetes.

### Quick Start
Provide your circuit and a small YAML config:

```bash
qsg build examples/bell_qiskit.py --config examples/config.yaml
```

If `--config` is omitted, QGen will attempt a best-effort language/provider
detection based on the source file.

## Current Capabilities
- Transpile circuits to intermediate representations such as QIR or OpenQASM 3.
- Inject provider-specific wrappers using Jinja2 templates.
- Build optimized container images for execution on IBM, Azure Quantum, Rigetti, and Amazon Braket backends.

## Design Overview
The design emphasizes modular components:
- **Input and Configuration**: Users provide their quantum code and a configuration file declaring the target provider and execution mode. Future versions will auto‑detect the programming language and select the appropriate template.
- **Template & Code Generation**: QGen maintains templates for each language/provider pair and generates runnable jobs by injecting authentication, transpilation, and API calls.
- **Containerization**: Generated code and dependencies are packaged using modern container build tools with layered caching.

Additional considerations include extensibility for new providers, static validation of generated code, session-based execution for lower latency, and secure handling of credentials.

See [docs/architecture.md](docs/architecture.md) for detailed architecture notes.
