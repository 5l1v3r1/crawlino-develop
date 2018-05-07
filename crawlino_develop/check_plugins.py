import os
import re
import tempfile

from typing import List, Tuple
from colored import fore, style, back
from contextlib import redirect_stdout
from distutils.version import StrictVersion

from pytest import main as main_pytest

from crawlino_develop.helpers import get_plugins
from crawlino_develop.model import CRDRunningConfig

DOC_SECTIONS = ("quick start", "requisites", "yaml config", "examples",
                "input data", "output data")
REQUIRED_FILES = ("__init__.py", "README.rst", "requirements.txt", "VERSION")
ACCEPTED_COVERAGE = 95


def _get_plugin_name(path) -> str:
    return os.sep.join(path.split(os.sep)[-2:])


def _check_required_files(plugin_path: str) -> List[Tuple[str, str]]:
    """This check ensures that a plugin contains the required files"""
    plugin_name = _get_plugin_name(plugin_path)
    plugin_files = os.listdir(plugin_path)

    issues = []
    for f in REQUIRED_FILES:
        if f not in plugin_files:
            issues.append((
                f"'{plugin_name}' - missing '{f}' file",
                "fail"
            ))
        else:
            issues.append((
                f"'{plugin_name}' - contain '{f}' file",
                "ok"
            ))

    # Check for test file
    if not any(x.startswith("test_") and x.endswith(".py")
               for x in plugin_files):
        issues.append((
            f"'{plugin_name}' - missing unit testing file (test_xxxxx.py)",
            "fail"
        ))
    else:
        issues.append((
            f"'{plugin_name}' - contains a unit testing file (test_xxxxx.py)",
            "ok"
        ))

    return issues


def _check_doc(plugin_path: str) -> List[Tuple[str, str]]:
    """this plugin checks that the plugin doc contains the minimum sections"""
    # load readme
    plugin_name = _get_plugin_name(plugin_path)

    results = []
    total_founds = []
    try:
        with open(os.path.join(plugin_path, "README.rst"), "r") as f:
            readme_file = f.read()

            # Build regex
            for section in DOC_SECTIONS:

                res = re.search(fr'''({section}[\w\s]*)([\s])([\-]+)''',
                                readme_file.lower())

                if res:
                    results.append((
                        f"'{plugin_name}' - Section "
                        f"'{section}' found in README.rst ",
                        "ok"
                    ))
                    total_founds.append(section)

        for not_found in set(DOC_SECTIONS).difference(total_founds):
            results.append(
                (f"'{plugin_name}' - Section '{not_found}' not found in "
                 f"README.rst", "fail")
            )

        return results

    except IOError:
        return [(f"'{plugin_name}' - Missing 'README.rst",
                 "fails")]


def _check_unit_tests(plugin_path: str) -> List[Tuple[str, str]]:
    # Get test form package installation dir
    # test_paths = os.path.join(os.path.dirname(crawlino_develop.__file__),
    #                           "tests")
    plugin_name = _get_plugin_name(plugin_path)

    ret = []

    try:
        with tempfile.NamedTemporaryFile() as f:

            # Launch PyTest and store results in a temporal file
            with redirect_stdout(open(f.name, 'w')):
                pytest_return = main_pytest([
                    f"--cov={plugin_path}", plugin_path
                ])

            # Load coverage results
            with open(f.name, "r") as r:
                results = r.read()

            # Get total coverage
            cov = re.search(r'''(TOTAL.*)( [\d]{1,3})(%)''', results)
            if not cov:
                ret.append((f"'{plugin_name}' - Can't obtain the coverage",
                            "fail"))
            else:
                cov_value = int(cov.group(2))

                if cov_value < ACCEPTED_COVERAGE:
                    ret.append((
                        f"'{plugin_name}' - Testing coverage is "
                        f"'{cov_value}%'. Must be greater than "
                        f"'{ACCEPTED_COVERAGE}%'",
                        "fail"
                    ))
                else:
                    ret.append((
                        f"'{plugin_name}' - Testing coverage is "
                        f"'{cov_value}%'",
                        "ok"
                    ))

    except Exception as e:
        ret.append((f"'{plugin_name}' - error running pytest", "fail"))
        return ret

    #
    # Pytest codes:
    #   https://docs.pytest.org/en/latest/usage.html#possible-exit-codes
    #
    if pytest_return == 0:
        ret.append((f"'{plugin_name}' - unit tests pass", "ok"))

    elif pytest_return == 1:
        ret.append((f"'{plugin_name}' - unit tests wasn't pass", "fail"))

    elif pytest_return == 5:
        ret.append((f"'{plugin_name}': can't find any tests to pass", "fail"))

    else:
        # Pytest error
        ret.append((f"'{plugin_name}': error running pytest", "fail"))

    return ret


def _check_version_format(plugin_path: str) -> List[Tuple[str, str]]:
    """This function checks the format for the VERSION file content

    Examples:
        - 1.0 -> OK
        - 1.0.0 -> OK
        - 1.1.2 -> OK
        - version1 -> BAD
        - pre-release-10 -> BAD
    """
    plugin_name = _get_plugin_name(plugin_path)

    try:
        with open(os.path.join(plugin_path, "VERSION"), "r") as f:
            version = f.readline()
    except FileNotFoundError:
        return [(f"'{plugin_name}' - missing 'VERSION' file", "fail")]

    try:
        StrictVersion(version)

        return [(f"'{plugin_name}' - Version '{version}'", "ok")]
    except ValueError:
        return [(f"'{plugin_name}' - Invalid version "
                 f"value '{version}' in 'VERSION' file ", "fail")]


def pass_plugins_checks(config: CRDRunningConfig) -> List[str]:
    """
    Launch all checks for each plugin

    return a list of issues
    """
    if isinstance(config.path, list):
        plugins_paths = config.path
    else:
        plugins_paths = [config.path]

    issues = []

    for path in plugins_paths:
        for plugin_path in get_plugins(path):
            # Check files
            issues.extend(_check_required_files(plugin_path))

            # Check doc
            issues.extend(_check_doc(plugin_path))

            # Check version format
            issues.extend(_check_version_format(plugin_path))

            # Launch unit-test
            issues.extend(_check_unit_tests(plugin_path))

    # List issues
    bad_issues = 0
    for description, status in issues:
        if status == "ok":
            if not config.show_all:
                continue

            color_start = fore.LIGHT_BLUE
            start_symbol = "[OK]"
            background = style.RESET
        else:
            bad_issues += 1
            start_symbol = "[FAIL]"
            color_start = fore.LIGHT_RED
            background = style.RESET + back.RED

        print(color_start,
              start_symbol,
              background,
              fore.WHITE,
              description,
              style.RESET)

    if bad_issues == 0:
        color_start = fore.LIGHT_BLUE
        start_symbol = "[OK]"
        background = style.RESET

        print(color_start,
              start_symbol,
              background,
              fore.WHITE,
              "The plugin is ready!",
              style.RESET)

    exit(len(issues))
