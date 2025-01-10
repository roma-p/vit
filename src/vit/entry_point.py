import sys
from vit.cli import logger
from vit.cli import cli_main


def main():
    print("aa")
    logger.setup()
    print(logger.log)
    print("aa")
    parser = cli_main.create_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        s = args.func(args)
        if s:
            sys.exit(0)
        else:
            sys.exit(1)
    sys.exit(0)
