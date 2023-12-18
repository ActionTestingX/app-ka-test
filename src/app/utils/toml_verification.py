"""This module is used to verify the toml file for the action."""
import base64
import json
import os
import subprocess

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


def check_toml2():
    def set_output(name, value):
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            print(f"{name}={value}", file=fh)

    label_names = json.loads(os.environ["LABELS"])
    rel_labels = {label for label in label_names if label.startswith("release-")}
    if len(rel_labels) == 0:
        rel_labels.add("release-skip")

    # Command to execute
    command = ["semantic-release", "--config", os.getenv("TOML_FILE"), "--noop", "version"]

    # verify labels and only run version calculation if its a release
    # if skip we do not return any version/set is_release to true
    # if more then one label we do not return any version//set is_release to true

    release_label_map = {
        "release-skip": "",
        "release-auto": "",
        "release-patch": "--patch",
        "release-minor": "--minor",
        "release-major": "--major",
    }

    valid_labels = set(release_label_map.keys())
    release_labels_found = len(valid_labels.intersection(rel_labels))
    if release_labels_found != 1:
        if len(rel_labels) > 1:
            print("Multiple release labels found, please only use one release label")
        else:
            print("No valid release label found, please use one of:")
            print(valid_labels)
        # exit, if multiple is set, then something is wrong and we really do not want to do any release
        exit(1)

    release_label = list(rel_labels)[0]
    forced_release = release_label_map[release_label]

    # temp debug..
    print(rel_labels)
    print(release_labels_found)
    print(release_label)
    print(forced_release)
    print(os.getenv("LATEST_RELEASE_TAG"))

    if release_label == "release-skip":
        # exit if skip release
        exit(0)

    if forced_release != "":
        command.append(forced_release)

    # debug print
    print(command)

    # Running the command and capturing output
    result = subprocess.run(command, capture_output=True, text=True)

    # Extracting the output
    output = result.stdout.strip()

    # print any errors
    if result.stderr:
        print(result.stderr)

    # The version name should be in the output
    print(f'Captured Version Name: "{output}"')

    # Compare current tag with new so we know if its new

    cur_version = os.getenv("LATEST_RELEASE_TAG")
    new_version = f"v{output}"

    # debug print
    print(cur_version)
    print(new_version)

    if cur_version != new_version:
        set_output("new_version", str(output))
        set_output("release_override_found", forced_release)
        set_output("is_release", "true")


if __name__ == "__main__":
    os.environ["CONFIG_TOML_FILE"] = r"C:\AibelProgs\code\app-ka-test\action_config.toml"
    os.environ["LABELS"] = '["release-auto"]'
    check_toml2()
