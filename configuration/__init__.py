import subprocess
import json
import string
import random

EVAL_FILE_CONTENT = """
let
  lib = import <nixpkgs/lib>;

  worldData = import {};

  result = lib.evalModules {{
    modules = [
      ./configuration/world-module.nix
      {{ world = worldData; }}
    ];
  }};
in
result.config.world
"""


def random_str():
    return "".join(random.choices(string.ascii_letters, k=32))


def load_config(file_name):
    expr = EVAL_FILE_CONTENT.format(file_name)

    result = subprocess.run(
        ["nix", "eval", "--expr", expr, "--json", "--impure"],
        capture_output=True,
        text=True,
    )

    try:
        result.check_returncode()
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        print(result.stderr)
        exit(1)
