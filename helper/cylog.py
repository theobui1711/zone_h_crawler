import logging
import time
import traceback
from logging.handlers import RotatingFileHandler

from slacker import Slacker


class CyLog:
    slack = None
    channel = None

    @staticmethod
    def __init__(slack_token, channel):
        format = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        format.converter = time.gmtime
        logging.basicConfig(level=logging.INFO, format=format)
        logging.disable(logging.DEBUG)

        for handler in logging.getLogger().handlers:
            logging.getLogger().removeHandler(handler)
            logging.getLogger("pika").propagate = False

        ch = logging.StreamHandler()
        ch.setFormatter(format)
        logging.getLogger().addHandler(ch)

        CyLog.slack = Slacker(slack_token)
        CyLog.channel = channel

    @staticmethod
    def info(msg):
        logging.info(msg)

    @staticmethod
    def error(trace=None):
        if trace is None:
            trace = traceback.print_exc()
        logging.error(trace)
        try:
            CyLog.slack.chat.post_message(CyLog.channel, trace)
        except Exception:
            logging.error(traceback.print_exc())
