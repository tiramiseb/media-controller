# Default modules
import configparser
import logging
import threading

# Dependencies
import zmq

################################################################################

class StopPlugin(Exception):
    pass

################################################################################

class Plugin:
    def __init__(self, conf, section, *args, **kwargs):
        self.configparser = conf
        self.section = section
        self.thread = threading.Thread(target=self.__loop)

    def run(self):
        self.thread.start()
        logging.info('Started plugin from section [{}]'.format(self.section))

    def __loop(self):
        try:
            self.loop()
        except StopPlugin:
            logging.error(
                'Stopping plugin from section [{}] because of a '
                'previous error'.format(self.section)
            )

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


class SenderPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.outsock = zmq.Context.instance().socket(zmq.PUB)
        self.outsock.connect("inproc://fromplugin")

    def loop(self):
        logging.error('No loop in plugin {}'.format(self.__class__.__name__))
        raise NotImplementedError

    def send(self, message):
        self.outsock.send_string(message)



class ReceiverPlugin(Plugin):
    messagefilter = ('',)
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.insock = zmq.Context.instance().socket(zmq.SUB)
        for filter_ in self.messagefilters:
            self.insock.setsockopt_string(zmq.SUBSCRIBE, filter_)
        self.insock.connect("inproc://toplugin")

    def loop(self):
        while True:
            self.receive(self.insock.recv_string())

    def receive(self, message):
        logging.error('No receiver in plugin {}'.format(
                                                       self.__class__.__name__))
        raise NotImplementedError