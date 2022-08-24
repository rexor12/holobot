# The concept for our semantic versioning is based on the format of the branch names:
# - main: the head of the code with the latest, next-gen development
# - develop/major.minor: the branch that targets the specified major-minor pair (no patches)
# - develop/major.minor.patch: the branch that targets the specified major-minor pair with patches
# Therefore, if you want a new version, just create a new develop branch.

import re
import subprocess

from holobot.sdk.system.models import Version

VERSION_PATH = "VERSION"
DEVELOP_BRANCH_REGEX = re.compile(r"develop/(\d+)\.(\d+)\.(\d+)", re.ASCII)

def read_output(command: str) -> str:
    return subprocess.check_output(command.split()).strip().decode()

def main() -> None:
    branch_name = read_output("git branch --show-current")
    if not (match := DEVELOP_BRANCH_REGEX.fullmatch(branch_name)):
        raise ValueError("Script must be run on develop branch.")

    major_minor_patch = map(int, match.groups())
    commit_count = int(read_output("git rev-list --count HEAD"))
    version = Version(*major_minor_patch, build=commit_count)

    with open(VERSION_PATH, "w") as f:
        f.write(str(version))
    print(f"New version: {version}")


if __name__ == "__main__":
    main()
