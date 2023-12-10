"""This module is used to verify the toml file for the action."""
import base64
import json
import os
import pathlib

import toml


def check_toml():
    """A test function docstring."""

    def set_output(name, value, encode_it=False):
        """A test function docstring."""
        if encode_it:
            value = base64.b64encode(value.encode("utf-8")).decode("utf-8")
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            print(f"{name}={value}", file=fh)

    data = toml.load(os.getenv("CONFIG_TOML_FILE"))

    # Evaluate all docker configs
    docker_config_list = data["tool"].get("docker", [])
    docker_enabled = False
    for docker_config in docker_config_list:
        if docker_config["enabled"]:
            docker_enabled = True
            break
    set_output("docker_enabled", docker_enabled)

    # Evalute all gitops configs
    gitops_config_list = data["tool"].get("gitops", [])
    gitops_enabled = False
    for gitops_config in gitops_config_list:
        if gitops_config["enabled"]:
            gitops_enabled = True
            break
    set_output("gitops_enabled", gitops_enabled)

    set_output("json_enabled", data["tool"]["json"]["enabled"])

    pip_tool = data["tool"].get("pip", None)
    if pip_tool is None:
        pip_enabled = False
    else:
        pip_enabled = data["tool"]["pip"]["enabled"]

    conda_tool = data["tool"].get("conda", None)
    if conda_tool is None:
        conda_enabled = False
    else:
        conda_enabled = data["tool"]["conda"]["enabled"]

    python_enabled = pip_enabled or conda_enabled

    set_output("python_enabled", python_enabled)
    set_output("pip_enabled", pip_enabled)
    set_output("conda_enabled", conda_enabled)

    set_output("toml_data", json.dumps(data), True)
    if python_enabled:
        pyproject_toml = os.getenv("PYPROJECT_TOML_FILE")
        py_data = toml.load(pyproject_toml)
        set_output("py_data", json.dumps(py_data), True)
