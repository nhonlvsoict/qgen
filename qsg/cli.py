from pathlib import Path
from typing import List

import typer

from qsg.ir.lower import lower_to_ir
from qsg.adapters import base as adapters_base
from qsg.container.docker import build_image
from qsg.config import BuildConfig

app = typer.Typer(help="QGen - Quantum Service Generator")

@app.command()
def build(
    src: str = typer.Argument(..., help="Quantum source file"),
    target: str = typer.Option(None, "--target", "-t", help="azure|rigetti|ibm|braket"),
    image: str = typer.Option(None, "--image", "-i", help="OCI image tag to produce"),
    profile: str = typer.Option("base", help="QIR profile for QIR targets"),
    workdir: str = typer.Option(".qsg_build", help="Build output dir"),
    execution_mode: str = typer.Option("job", help="Execution mode such as job or session"),
    config: Path = typer.Option(None, "--config", "-c", help="Path to build configuration file"),
):
    if config:
        cfg = BuildConfig.from_file(config)
        if image is not None:
            cfg.image = image  # Override image if specified
    else:
        if target is None:
            from qsg.detect import detect_language_and_provider
            _, detected_target = detect_language_and_provider(src)
            target = detected_target
        if target is None:
            raise typer.BadParameter("Target provider must be specified via --target or --config")
        cfg = BuildConfig(target=target, profile=profile, image=image, workdir=workdir, execution_mode=execution_mode)

    adapter = adapters_base.load_adapter(cfg.target, profile=cfg.profile)
    ir_artifact = lower_to_ir(src, adapter.required_ir())
    payload = adapter.prepare_payload(ir_artifact)

    tag = build_image(adapter, payload, image=cfg.image, workdir=cfg.workdir)
    typer.echo(f"Built {tag}")

@app.command()
def run_local(
    image: str,
    env: List[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variables in KEY=VALUE format.",
    ),
):
    """Run the container locally for a smoke test (simulated)."""
    import docker

    client = docker.from_env()
    env_dict = dict(item.split("=", 1) for item in env) if env else None
    logs = client.containers.run(
        image, detach=False, remove=True, environment=env_dict
    )
    print(logs.decode() if isinstance(logs, (bytes, bytearray)) else logs)

if __name__ == "__main__":
    app()
