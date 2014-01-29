# Default modules
import configparser
import logging
import queue
import threading

################################################################################

class StopPlugin(Exception):
    pass

################################################################################

class Plugin:
    def __init__(self, conf, section, queue_to_hub, *args, **kwargs):
        self.configparser = conf
        self.section = section
        self.outqueue = queue_to_hub
        self.inqueue = queue.Queue()
        self.thread = threading.Thread(target=self.__loop)
        self.thread.daemon = True

    def run(self):
        logging.info('Starting plugin from section [{}]'.format(self.section))
        self.thread.start()

    def __loop(self):
        try:
            self.loop()
        except StopPlugin:
            logging.error(
                'Stopping plugin from section [{}] because of a '
                'previous error'.format(self.section)
            )

    def send(self, message):
        """Send message to the hub, which will dispatch to all plugins"""
        self.outqueue.put(message)

    def conf(self, key, default=None):
        try:
            return self.configparser.get(self.section, key)
        except configparser.NoOptionError:
            if default:
                return default
            else:
                logging.error(
                    'No option "{}" found in section [{}]'.format(
                        key, self.section
                    )
                )
                raise StopPlugin

    def allconf(self):
        return self.configparser.items(self.section)

    def error(self, msg):
        logging.error(msg)
        raise StopPlugin

    def loop(self):
        """Override this in a sender plugin"""
        while True:
            self.receive(self.inqueue.get())

    def receive(self, message):
        """Override this in a receiver plugin"""
        pass