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


def _bump_data(repo: Repo = Repo(), bump_type: str = "patch") -> dict:
    latest_tag = repo.tags[-1]

    latest_version = version_from_tag(latest_tag)
    latest_version_semver = semver.VersionInfo.parse(latest_version)

    try:
        bump_function = getattr(latest_version_semver, f"bump_{bump_type}")
    except AttributeError as e:
        raise Exception(f"Incorrect bump type passed: {bump_type}") from e

    next_version = bump_function()
    next_tag = f"v{str(next_version)}"

    return {
        "latest_tag": str(latest_tag),
        "latest_version": latest_version,
        "next_tag": next_tag,
        "next_version": str(next_version),
    }


def bump_patch() -> str:
    data = _bump_data(Repo(), "patch")
    print(json.dumps(data))


def bump_minor() -> str:
    data = _bump_data(Repo(), "minor")
    print(json.dumps(data))


def bump_major() -> str:
    data = _bump_data(Repo(), "major")
    print(json.dumps(data))


if __name__ == "__main__":
    repo = Repo()
    if len(sys.argv) == 1:
        bump_patch()
    else:
        print(json.dumps(_bump_data(repo, sys.argv[1])))
