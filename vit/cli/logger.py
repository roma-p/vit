import logging


def setup(verbose=False):
    global log
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig()
    log = logging.getLogger("vit")
    log.setLevel(log_level)
