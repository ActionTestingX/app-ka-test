import os

from app.utils.toml_verification import check_toml


def test_basic_toml_check(root_dir):
    action_toml = root_dir / "action_config.toml"
    os.environ["GITHUB_OUTPUT"] = "temp/output.txt"
    os.environ["CONFIG_TOML_FILE"] = action_toml.as_posix()
    os.environ["PYPROJECT_TOML_FILE"] = (root_dir / "pyproject.toml").as_posix()
    os.makedirs(os.path.dirname(os.environ["GITHUB_OUTPUT"]), exist_ok=True)
    check_toml()
