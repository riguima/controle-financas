from pathlib import Path

import toml


def get_config():
    config = toml.load(open(Path(__file__).parent.parent / ".config.toml"))
    return config["testing"] if config["TESTING"] else config["default"]
