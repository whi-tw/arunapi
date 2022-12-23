#!/usr/bin/env python
import json
import sys

import semver
from git import Repo, TagReference


def version_from_tag(tag: TagReference) -> str:
    tag = str(tag)
    if tag[0] == "v":
        return tag[1:]
    else:
        return tag


def main(repo: Repo, bump_type: str = "patch"):
    latest_tag = repo.tags[-1]

    latest_version = version_from_tag(latest_tag)
    latest_version_semver = semver.VersionInfo.parse(latest_version)

    try:
        bump_function = getattr(latest_version_semver, f"bump_{bump_type}")
    except AttributeError as e:
        raise Exception(f"Incorrect bump type passed: {bump_type}") from e

    next_version = bump_function()
    next_tag = f"v{str(next_version)}"

    output_data = {
        "latest_tag": str(latest_tag),
        "latest_version": latest_version,
        "next_tag": next_tag,
        "next_version": str(next_version),
    }

    print(json.dumps(output_data))


if __name__ == "__main__":
    repo = Repo()
    if len(sys.argv) == 1:
        main(repo)
    else:
        main(repo, sys.argv[1])
