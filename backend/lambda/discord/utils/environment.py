import logging
import os
import sys
import threading
from dotenv import load_dotenv

thread_local = threading.local()


class PathTruncatingFormatter(logging.Formatter):
    def format(self, record):
        """Logging Formatter subclass to truncate the pathname to the two innermost directories."""
        if 'pathname' in record.__dict__.keys():
            fullpath = record.pathname
            pathparts = fullpath.split('/')
            if len(pathparts) >= 2:
                trunc_path = './{}/{}'.format(pathparts[-2], pathparts[-1])
            else:
                trunc_path = fullpath
            record.pathname = trunc_path

        return super(PathTruncatingFormatter, self).format(record)


def init_env():
    if os.getenv('AWS_EXECUTION_ENV') is None:
        print('Operating in local context, loading .env file...')
        load_dotenv("../../../.env", verbose=True)
    else:
        print('Operating in Lambda context...')

    logger = init_logger()

    return logger


def init_logger():
    logger = getattr(thread_local, 'logger', None)
    if logger is not None:
        return logger

    if os.getenv('LOCAL_LOG_FORMAT') is None:
        local_log_format = \
            '%(asctime)-26s [%(levelname)-5s] %(name)-25s %(pathname)s:%(lineno)s %(message)s'
    else:
        local_log_format = os.getenv('LOCAL_LOG_FORMAT')
    aws_log_format = '[%(levelname)s] %(name)-25s %(pathname)s:%(lineno)s %(message)s'

    log_level = logging.INFO

    if os.getenv('AWS_EXECUTION_ENV') is None:
        # NOTE: Local Dev, this formatter will be respected
        new_format = local_log_format
        logging.basicConfig(stream=sys.stdout,
                            format=new_format,
                            level=log_level)
    else:
        # NOTE: AWS has already mutated the logger, so we might want to adjust it.
        new_format = aws_log_format
        logging.basicConfig(format=aws_log_format,
                            level=log_level)

    for h in logging.root.handlers:
        h.setFormatter(PathTruncatingFormatter(new_format))

    # Our default level is WARN...
    logging.root.setLevel(logging.WARN)

    #
    # This will adjust all logging to DEBUG.  It's very loud.
    # However, you can see all subsystems and then selectively enable the
    # various subsystems you really want verbose logging out of.
    #
    # logging.root.setLevel(logging.DEBUG)
    #

    logger = logging.getLogger('')
    logger.setLevel(log_level)
    logger.info('Initialized Logger...')

    # These are some common loggers that can be enabled.
    # urllib3.connectionpool
    # boto3.resources.factory
    # botocore.hooks
    # botocore.utils
    # botocore.parsers
    # botocore.endpoint
    # botocore.auth
    # botocore.retryHandler
    # botocore.retries.standard

    #
    # Enable the retry handler, because we should not really have any.
    #
    logging.getLogger('botocore.retries.standard').setLevel(logging.INFO)
    logging.getLogger('botocore.retryHandler').setLevel(logging.INFO)

    #
    # This will enable the aws client debug level to be louder.
    #
    # logging.getLogger('boto3').setLevel(logging.DEBUG)
    return logger


def maybe_init_context():
    if os.getenv('FORKED_PROCESS') != "True":
        if os.getenv('AWS_EXECUTION_ENV') is None:
            if os.getenv('LAMBDA_EVENT_DATA') is not None:
                event = json.loads(os.getenv('LAMBDA_EVENT_DATA').replace('\\\"', '"'))
            else:
                event = {}
            lambda_handler(event, {})