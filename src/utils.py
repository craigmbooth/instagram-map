import timeit

class TimedLogger(object):
    """Context manager prints out how long it took for a code block to
    execute to the logfile

    with TimedLogger(message):
        codeblock

    will either print "message (took X.XXs)" or if the TimedLogger was
    initialized with a logger, will write it to that log.
    """

    def __init__(self, msg, logger=None):
        self.logger = logger
        self.base_msg = msg

    def __enter__(self):
        """Begin timing when you enter the context manager"""
        self.start = timeit.default_timer()

    def __exit__(self, *args):
        """End timing and write timed ``msg`` to the log"""
        self.end = timeit.default_timer()

        interval = self.end - self.start
        msg = "".join([self.base_msg," (took ", str(interval), "s)"])

        if self.logger is None:
            print msg
        else:
            self.logger.info(msg)
