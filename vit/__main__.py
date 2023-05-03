import sys
import logging
from vit.cli import cli_main

logging.basicConfig()
log = logging.getLogger("vit")
log.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = cli_main.create_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        s = args.func(args)
        if s:
            sys.exit(0)
        else:
            sys.exit(1)
    sys.exit(0)
