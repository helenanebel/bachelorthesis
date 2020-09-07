import sys
import os
import logging
from datetime import datetime

logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%d-%b-%Y")

logfile = 'logfiles_debugging/logfile_' + timestampStr

logger = logging.getLogger()


def write(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    error_message = 'Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(c=type(e).__name__, m=str(e), t=exc_type, f=filename, line=exc_tb.tb_lineno)
    logger.debug(error_message)


def comment(comment_string):
    logger.debug(comment_string)