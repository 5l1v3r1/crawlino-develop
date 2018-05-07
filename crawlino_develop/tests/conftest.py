import os
import pytest
import os.path as op


from typing import Dict, List, Tuple
from os.path import abspath, join, dirname


@pytest.fixture
def plugins_files() -> List[Tuple[str, Tuple]]:
    """
    [
        {"plugin_type/plugin_dir_name": ("file1", "file2", "file3", ...)}
    ]
    """

    res = []

    plugins_base_path = op.abspath(op.join(dirname(__file__), ".."))

    for root, dirs, files in os.walk(plugins_base_path):
        if root.endswith("tests"):
            continue

        # Only get the first folder of each plugin:
        # input_plugins/input_web_plugin/
        if root.split("/")[-2].endswith("_plugins"):
            res.append((
                f'{root.split("/")[-2]}/{root.split("/")[-1]}', files
            ))

    return res


if __name__ == '__main__':
    plugins_files()
