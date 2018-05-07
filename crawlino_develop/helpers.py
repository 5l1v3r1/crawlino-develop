import os
import os.path as op

from typing import List


def get_plugins(path) -> List[str]:
    """
    returns:

    [ "/my/plugin/path", "/my/other/plugin/path"]
    """

    res = []

    for root, dirs, files in os.walk(op.abspath(path)):
        if root.endswith("tests"):
            continue

        # Only get the first folder of each plugin:
        # input_plugins/input_web_plugin/
        if root.split("/")[-2].endswith("_plugins"):
            res.append(root)

    return res
