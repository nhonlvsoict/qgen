from dataclasses import dataclass
from pathlib import Path
import json
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass
class BuildConfig:
    """Configuration options for building a QGen image."""

    target: str
    profile: str = "base"
    image: str | None = None
    workdir: str = ".qsg_build"
    execution_mode: str = "job"

    @classmethod
    def from_file(cls, path: str | Path) -> "BuildConfig":
        """Load build configuration from a JSON or YAML file."""
        p = Path(path)
        text = p.read_text()
        if p.suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("pyyaml is required to parse YAML config files")
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(text)
        return cls(**data)
