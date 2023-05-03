import sys
import argparse
from collections import namedtuple


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kw):
        super(ArgumentParser, self).__init__(*args, **kw)
        if not hasattr(self, "shared_args"):
            self.shared_args = {}

        # Add arguments from the shared ones
        for a in self.shared_args.values():
            super(ArgumentParser, self).add_argument(*a.args, **a.kwargs)

    def add_argument(self, *args, **kw):
        shared = kw.pop("shared", False)
        res = super(ArgumentParser, self).add_argument(*args, **kw)
        if shared:
            action = kw.get("action")
            if (action) not in ("store", "store_true"):
                raise NotImplementedError(
                    "Action {} for {} is not supported".format(action, args)
                )
            # Take note of the argument if it was marked as shared
            self.shared_args[res.dest] = SharedArgument(res, args, kw)
        return res

    def add_subparsers(self, *args, **kw):
        if "parser_class" not in kw:
            kw["parser_class"] = type(
                "ArgumentParser",
                (self.__class__,),
                {"shared_args": dict(self.shared_args)}
            )
        return super(ArgumentParser, self).add_subparsers(*args, **kw)

    def parse_args(self, *args, **kw):
        if "namespace" not in kw:
            # Use a subclass to pass the special action list without making it
            # appear as an argument
            kw["namespace"] = type(
                "Namespace", (Namespace,),
                {"_shared_args": self.shared_args})()
        return super(ArgumentParser, self).parse_args(*args, **kw)

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


# -- PRIVATE -----------------------------------------------------------------

def add_existing_parser(self, argument_parser, name, **kwargs):

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
setattr(argparse._SubParsersAction, "add_existing_parser", add_existing_parser)


SharedArgument = namedtuple("SharedArgument", ["action", "args", "kwargs"])


class ArgumentError(Exception):
    pass


class Namespace(argparse.Namespace):

    def __setattr__(self, name, value):
        arg = self._shared_args.get(name)
        if (arg):
            action_type = arg.kwargs.get("action")
            if action_type == "store_true":
                # OR values
                old = getattr(self, name, False)
                super(Namespace, self).__setattr__(name, old or value)
            elif action_type == "store":
                old = getattr(self, name, False)
                if old is None:
                    super(Namespace, self).__setattr__(name, value)
                elif old != value:
                    raise argparse.ArgumentError(
                        "conflicting values provided for {} ({} and {})".format(
                            arg.action.dest,
                            old,
                            value
                        )
                    )
                else:
                    raise NotImplementedError(
                        "Action {} for {} is not supported".format(
                            action_type,
                            arg.action
                        )
                    )
            else:
                return super(Namespace, self).__setattr__(name, value)
