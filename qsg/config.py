from dataclasses import dataclass

@dataclass
class BuildConfig:
    target: str
    profile: str = "base"
    image: str | None = None
    workdir: str = ".qsg_build"
