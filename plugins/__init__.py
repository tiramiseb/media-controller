# Default modules
import logging
import threading

# Dependencies
import zmq

################################################################################

class Plugin:

    def __init__(self, conf, section, *args, **kwargs):
        self.conf = conf
        self.sectionname = section
        self.thread = threading.Thread(target=self.loop)

    def run(self):
        self.thread.start()



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
        self.insock = kwargs['zmq_context'].socket(zmq.SUB)
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