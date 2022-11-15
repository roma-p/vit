import os
from vit.custom_exceptions import VitCustomException
from vit import constants

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def is_vit_repo():
    current_path = os.getcwd()
    s = os.path.exists(
        os.path.join(
            current_path,
            constants.VIT_DIR
        )
    )
    if not s:
        log.error("{} is not a vit repository".format(current_path))
    return s


def execute_vit_command(vit_command_func, error_mess, *args, **kargs):
    if not is_vit_repo():
        return False, None
    try:
        ret = vit_command_func(os.getcwd(), *args, **kargs)
    except VitCustomException as e:
        log.error(error_mess)
        log.error(str(e))
        return False, None
    else:
        return True, ret


def add_parser(subparser, argument_parser, name, **kwargs):

    if name in subparser._name_parser_map:
        raise ArgumentError(subparser, _('conflicting subparser: %s') % name)

    aliases = kwargs.pop('aliases', ())
    for alias in aliases:
        if alias in subparser._name_parser_map:
            raise ArgumentError(
                subparser, _('conflicting subparser alias: %s') % alias)

    # create a pseudo-action to hold the choice help
    if 'help' in kwargs:
        help = kwargs.pop('help')
        choice_action = subparser._ChoicesPseudoAction(name, aliases, help)
        subparser._choices_actions.append(choice_action)

    subparser._name_parser_map[name] = argument_parser

    # make parser available under aliases also
    for alias in aliases:
        subparser._name_parser_map[alias] = argument_parser

