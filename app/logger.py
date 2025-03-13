import logging

logger = logging.getLogger()

fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
fh.setFormatter(fh_formatter)
fh.setLevel(logging.INFO)

logger.addHandler(fh)
logger.setLevel(logging.DEBUG)