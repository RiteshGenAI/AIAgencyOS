"""Deploy local code to AWS using Docker, ECR, and Terraform."""

import os
import subprocess
from pathlib import Path

PROJECT = os.environ.get("PROJECT", "ai-agency-os")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
IMAGE_TAG = os.environ.get("IMAGE_TAG", "latest")

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("\n$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def main() -> None:
    run(
        ["docker", "build", "-f", "docker/Dockerfile.backend", "-t", f"{PROJECT}-backend:{IMAGE_TAG}", "."],
        cwd=ROOT,
    )
    run(
        ["docker", "build", "-f", "docker/Dockerfile.agents", "-t", f"{PROJECT}-agents:{IMAGE_TAG}", "."],
        cwd=ROOT,
    )
    run(
        ["docker", "build", "-f", "docker/Dockerfile.frontend", "-t", f"{PROJECT}-frontend:{IMAGE_TAG}", "."],
        cwd=ROOT,
    )

    print("TODO: login to ECR and push images with the correct repository URIs")

    tf_dir = ROOT / "infra" / "terraform"
    run(["terraform", "init"], cwd=tf_dir)
    run(["terraform", "apply", "-auto-approve", f"-var=image_tag={IMAGE_TAG}"], cwd=tf_dir)


if __name__ == "__main__":
    main()
