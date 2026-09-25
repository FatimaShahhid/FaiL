from pathlib import Path


def load_identity(profile_name: str = "runtime_identity.md") -> str:
    """Load a FAiL identity profile."""

    profile_path = (
        Path(__file__).resolve().parent.parent
        / "memory"
        / "identity"
        / profile_name
    )

    if not profile_path.exists():
        raise FileNotFoundError(
            f"FAiL identity profile not found: {profile_path}"
        )

    return profile_path.read_text(encoding="utf-8")