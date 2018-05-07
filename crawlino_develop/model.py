from argparse import Namespace
from typing import List


class CRDRunningConfig:

    def __init__(self,
                 verbosity: bool,
                 path: List[str] or str,
                 show_all: bool = False):
        self.path = path
        self.verbosity = verbosity
        self.show_all = show_all

    @classmethod
    def from_argparser(cls, argparser_input: Namespace):
        return CRDRunningConfig(
            verbosity=argparser_input.verbosity,
            path=argparser_input.PATH,
            show_all=bool(argparser_input.show_all)
        )


__all__ = ("CRDRunningConfig",)
