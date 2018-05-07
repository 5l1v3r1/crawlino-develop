import argparse

from crawlino_develop.model import CRDRunningConfig
from crawlino_develop.check_plugins import pass_plugins_checks


def build_parser():
    parser = argparse.ArgumentParser(
        description='Crawlino-Develop: helping to contribute to Crawlino.org',
        formatter_class=argparse.RawTextHelpFormatter)

    # Main options
    parser.add_argument("-v", "--verbosity", dest="verbosity", action="count",
                        help="verbosity level: -v, -vv, -vvv.", default=3)

    subparsers = parser.add_subparsers(help='Options', dest="option")
    plugins_search_parser = subparsers.add_parser('plugin-check',
                                                  help='search plugin')
    plugins_search_parser.add_argument("PATH", nargs="+", default=".")
    plugins_search_parser.add_argument("--show-all",
                                       action="store_true",
                                       default=False)

    return parser


def main():
    parser = build_parser()
    parsed = parser.parse_args()

    if not parsed.option:
        print("[!] You must specify an action!")
        parser.print_help()
        return

    actions = {
        'plugin-check': pass_plugins_checks
    }

    # Load config
    config = CRDRunningConfig.from_argparser(parsed)

    try:
        actions[parsed.option](config)
    except KeyError as e:
        print("[!] Invalid action: ", e)
        return
    except KeyboardInterrupt:
        print("Finishing...")


if __name__ == '__main__':
    main()
