import deq_shapes


def test_distribution_name() -> None:
    assert deq_shapes.DISTRIBUTION_NAME == "deq-shapes"


def test_version_is_semver() -> None:
    major, minor, patch = deq_shapes.__version__.split(".")
    assert all(part.isdigit() for part in (major, minor, patch))
