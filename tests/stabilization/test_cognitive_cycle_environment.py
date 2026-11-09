from __future__ import annotations

from tools.run_cognitive_cycle_evidence import _environment_metadata


def test_environment_metadata_contains_reproducibility_fields() -> None:
    metadata = _environment_metadata()

    assert metadata["git_sha"]
    assert metadata["aurelia_package_version"]

    python = metadata["python"]
    assert python["version"]
    assert python["implementation"]

    platform = metadata["platform"]
    assert platform["system"]
    assert platform["release"]
    assert platform["machine"]
