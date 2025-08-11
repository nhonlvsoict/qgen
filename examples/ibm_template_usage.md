# IBM Template Usage

This example demonstrates how to render the IBM sampler wrapper with custom parameters.

```python
from qsg.adapters.template_manager import render

context = {
    "payload_path": "/tmp/custom.qasm",
    "token_env_var": "MY_IBM_TOKEN",
}
code = render("ibm_sampler.py.j2", context, required_fields=["payload_path", "token_env_var"])
print(code)
```

Running this snippet prints the fully rendered Python entrypoint with the supplied
`payload_path` and `token_env_var` values embedded.
