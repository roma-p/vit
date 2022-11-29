import sys
import logging
from vit.command_line_lib import args_parser

logging.basicConfig()
log = logging.getLogger("vit")
log.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = args_parser.create_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        s = args.func(args)
        if s: sys.exit(0)
        else: sys.exit(1)
    sys.exit(0)
