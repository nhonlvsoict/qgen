from pathlib import Path
import tempfile
import os
from jinja2 import Template
import docker

def build_image(adapter, payload: dict, image: str | None, workdir: str = ".qsg_build") -> str:
    work = Path(workdir)
    if work.exists():
        import shutil
        shutil.rmtree(work)
    work.mkdir(parents=True)

    # Write payload files
    payload_dir = work / "payload"
    payload_dir.mkdir()
    for name, content in payload.items():
        (payload_dir / name).write_text(content if isinstance(content, str) else content.decode(), encoding="utf-8")

    # Render entrypoint
    entrypoint_tpl = (Path(__file__).parent / "templates" / "entrypoint.sh.j2").read_text()
    entrypoint = Template(entrypoint_tpl).render(adapter_entrypoint=adapter.entrypoint())
    (work / "entrypoint.sh").write_text(entrypoint)
    os.chmod(work / "entrypoint.sh", 0o755)

    # Render Dockerfile
    dockerfile_tpl = (Path(__file__).parent / "templates" / "Dockerfile.j2").read_text()
    dockerfile = Template(dockerfile_tpl).render(runtime_packages=adapter.runtime_packages())
    (work / "Dockerfile").write_text(dockerfile)

    tag = image or f"qsg/{adapter.name}:local"
    client = docker.from_env()
    client.images.build(path=str(work), tag=tag)
    return tag
