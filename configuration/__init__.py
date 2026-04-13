import subprocess
import json
import string
import random
from pathlib import Path

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
    tmp_filename = f"tmp-{random_str()}.nix"
    with open(tmp_filename, "w") as f:
        f.write(EVAL_FILE_CONTENT.format((file_name)))

    result = subprocess.run(
        ["nix", "eval", "-f", tmp_filename, "--json"], capture_output=True, text=True
    )

    Path(tmp_filename).unlink(missing_ok=True)
    try:
        result.check_returncode()
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        print(result.stderr)
        exit(1)
