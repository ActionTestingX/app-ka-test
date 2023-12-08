"""Something here"""
import pathlib

import ruamel.yaml


def yaml_util(gitops_file: str, image_path: str, docker_image: str, kind: str):
    """Update yaml file with latest docker image"""

    yaml = ruamel.yaml.YAML()

    with open(gitops_file, "r") as f:
        yaml_blocks = list(yaml.load_all(f))

    # Update yaml kind blocks with latest image
    for block in yaml_blocks:
        if block["kind"] != kind:
            continue
        block[image_path] = docker_image

    with open(gitops_file, "w") as f:
        yaml.dump_all(yaml_blocks, f)


if __name__ == "__main__":
    code_dir = [p for p in pathlib.Path(__file__).parents if p.name == "code"][0]
    gitops_dir = code_dir / "gitops-ka-test"
    yaml_file = gitops_dir / "cluster_test/nginx-deployment-service.yaml"
    yaml_image_path = '["spec"]["template"]["spec"]["containers"][0]["image"]'

    yaml_util(yaml_file.as_posix(), yaml_image_path, "python-team/app-python:0.0.1", "Deployment")
