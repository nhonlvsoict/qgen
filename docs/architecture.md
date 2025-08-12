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

## 3. Template Variables and Provider Wrappers

Adapters use Jinja2 templates to build provider-specific entrypoints. Templates receive
variables through a context dictionary, and the environment is configured with
`StrictUndefined` so that missing variables surface as errors during rendering.

### Default Context Keys

The IBM sampler template (`qsg/adapters/templates/ibm_sampler.py.j2`) illustrates the
expected context keys:

- `payload_path`: path to the serialized circuit file. Defaults to
  `/app/payload/program.qasm`.
- `token_env_var`: name of the environment variable that carries the API token.
  Defaults to `IBM_TOKEN`.

Adapters may override these defaults by supplying their own context values. If a required
key is missing or falsy, `template_manager.render` raises a `ValueError`.

### Adding New Provider Wrappers

To introduce support for another provider:

1. **Create an `Adapter` subclass** under `qsg/adapters/` implementing
   `required_ir`, `prepare_payload`, `runtime_packages`, and `entrypoint`.
2. **Add a Jinja2 template** under `qsg/adapters/templates/` and render it in
   `entrypoint`, documenting all template variables and their defaults.
3. **Validate required fields** using `template_manager.render(..., required_fields=[...])`
   so missing context values fail fast.
4. **Write tests** that demonstrate both default behavior and custom overrides for the
   template variables.

