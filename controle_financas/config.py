import toml


def get_config(testing=False):
    config = toml.load(open(".config.toml"))
    return config["testing"] if testing else config["default"]
