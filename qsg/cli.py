import typer
from typing import List
from qsg.ir.lower import lower_to_ir
from qsg.adapters import base as adapters_base
from qsg.container.docker import build_image

app = typer.Typer(help="Quantum Service Generator")

@app.command()
def build(
    src: str = typer.Argument(..., help="Python quantum file (expects build_circuit() to return a QuantumCircuit)"),
    target: str = typer.Option(..., "--target", "-t", help="azure|rigetti|ibm|braket"),
    image: str = typer.Option(None, "--image", "-i", help="OCI image tag to produce"),
    profile: str = typer.Option("base", help="QIR profile for QIR targets"),
    workdir: str = typer.Option(".qsg_build", help="Build output dir")
):
    adapter = adapters_base.load_adapter(target, profile=profile)
    ir_artifact = lower_to_ir(src, adapter.required_ir())
    payload = adapter.prepare_payload(ir_artifact)

    tag = build_image(adapter, payload, image=image, workdir=workdir)
    typer.echo(f"Built {tag}")

@app.command()
def run_local(
    image: str,
    env: List[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variable(s) in KEY=VALUE format",
    ),
):
    """Run the container locally for a smoke test (simulated).

    Environment variables can be provided with ``-e/--env`` using the
    ``KEY=VALUE`` format and will be passed to the container.
    """
    import docker
    import os

    env_dict = {}
    if env:
        for item in env:
            if "=" in item:
                key, value = item.split("=", 1)
                env_dict[key] = value
            else:
                env_dict[item] = os.environ.get(item)

    client = docker.from_env()
    logs = client.containers.run(
        image, detach=False, remove=True, environment=env_dict or None
    )
    print(logs.decode() if isinstance(logs, (bytes, bytearray)) else logs)

if __name__ == "__main__":
    app()
