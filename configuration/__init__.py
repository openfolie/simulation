import subprocess
import json

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
