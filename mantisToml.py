import tomllib
import sys

def read_config():
    try:
        with open("mtif.toml", "rb") as f:
            config = tomllib.load(f)
        return config
    except FileNotFoundError:
        print("ERROR: mtif.toml not found.")
        sys.exit(1)
