import typer
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
def run_local(image: str):
    """Run the container locally for a smoke test (simulated)."""
    import docker
    client = docker.from_env()
    logs = client.containers.run(image, detach=False, remove=True)
    print(logs.decode() if isinstance(logs, (bytes, bytearray)) else logs)

if __name__ == "__main__":
    app()
