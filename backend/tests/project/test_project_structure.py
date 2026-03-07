import pathlib


SRC = pathlib.Path(__file__).parents[2] / "src" / "pilates"
TESTS = pathlib.Path(__file__).parents[1]


def test_unit_test_package_mirrors_project_structure():
    invalid_test_filepaths = _get_invalid_test_filepaths(TESTS / "unit")

    assert not invalid_test_filepaths, "\n".join(str(p) for p in invalid_test_filepaths)


def test_no_tests_files_present_in_source_code():
    test_files_in_source_code: list[pathlib.Path] = []

    for path in SRC.rglob("*"):
        if path.name.startswith("test_"):
            test_files_in_source_code.append(path)

    assert not test_files_in_source_code


def _get_invalid_test_filepaths(test_package: pathlib.Path) -> list[pathlib.Path]:
    invalid_paths: list[pathlib.Path] = []

    for test_filepath in test_package.rglob("test_*.py"):
        relative_path = test_filepath.relative_to(test_package)

        expected_filename = test_filepath.name.replace("test_", "")
        acceptable_srcs = [
            SRC / relative_path.parent / expected_filename,  # Public module.
            SRC / relative_path.parent / f"_{expected_filename}",  # Private module.
        ]

        if not any(path.exists() for path in acceptable_srcs):
            invalid_paths.append(test_filepath)

    return invalid_paths
