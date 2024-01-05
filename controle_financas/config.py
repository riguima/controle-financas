import toml


def get_config():
    config = toml.load(open(".config.toml"))
    return config["testing"] if config["TESTING"] else config["default"]
