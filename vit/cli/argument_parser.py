import sys
import argparse
from dataclasses import dataclass
from collections import namedtuple


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


@dataclass
class SubArgumentParserWrapper:
    sub_command_name: str = ""  # DELME
    arg_parser: argparse.ArgumentParser = None  # DELME
    help: str = ""  # DELME
    description: str = ""  # DELME
    epilog: str = ""  # DELME
    origin_connection_needed: bool = False
    may_not_be_up_to_date: bool = False


CONNECTION_NEEDED = "! Connection to origin repository needed."
NOT_UP_TO_DATE = """! This command only uses local metadata
! Update local metadata from origin using 'vit fetch' cmd.
"""
COMMON_EPILOG = ""


def add_subparser_from_parser_wrapper(
        subparser,
        sub_argument_wrapper):

    if sub_argument_wrapper.arg_parser.description is None:
        sub_argument_wrapper.arg_parser.description = ""
    if sub_argument_wrapper.arg_parser.epilog is None:
        sub_argument_wrapper.arg_parser.epilog = ""


    if sub_argument_wrapper.origin_connection_needed:
        sub_argument_wrapper.arg_parser.description += "\n"+CONNECTION_NEEDED
    if sub_argument_wrapper.may_not_be_up_to_date:
        sub_argument_wrapper.arg_parser.description += "\n"+NOT_UP_TO_DATE
    sub_argument_wrapper.arg_parser.epilog += "\n"+COMMON_EPILOG

    sub_argument_wrapper.arg_parser.formatter_class = argparse.RawDescriptionHelpFormatter

    subparser.add_existing_parser(
        sub_argument_wrapper.arg_parser,
        sub_argument_wrapper.arg_parser.prog,
    )


# -- PRIVATE -----------------------------------------------------------------

def _add_existing_parser(self, argument_parser, name, **kwargs):

    if name in self._name_parser_map:
        raise ArgumentError(self, ('conflicting subparser: %s') % name)

    aliases = kwargs.pop('aliases', ())
    for alias in aliases:
        if alias in self._name_parser_map:
            raise ArgumentError(
                self, ('conflicting subparser alias: %s') % alias)

    # create a pseudo-action to hold the choice help
    if 'help' in kwargs:
        help = kwargs.pop('help')
        choice_action = self._ChoicesPseudoAction(name, aliases, help)
        self._choices_actions.append(choice_action)

    self._name_parser_map[name] = argument_parser

    # make parser available under aliases also
    for alias in aliases:
        self._name_parser_map[alias] = argument_parser


# TODO: probably enherit this base class rather than monkey patch it.
setattr(
    argparse._SubParsersAction,
    "add_existing_parser",
    _add_existing_parser
)


SharedArgument = namedtuple("SharedArgument", ["action", "args", "kwargs"])


class ArgumentError(Exception):
    pass
