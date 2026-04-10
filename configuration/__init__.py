import subprocess
import json


def load_config():
    result = subprocess.run(
        ["nix", "eval", "-f", "default.nix", "--json"],
        capture_output=True,
        text=True
    )
    try:
        result.check_returncode()
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        print(result.stderr)
        exit(1)
