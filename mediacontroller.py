#!/usr/bin/env python3

# Default modules
import configparser
import importlib
import logging
import queue
import sys
import threading

# Dependencies
from daemonize import Daemonize

################################################################################
# Default values

class DEFAULTS:
    configfile='mediacontroller.conf'
    pidfile='mediacontroller.pid'
    loglevel='info'

################################################################################
# The code

class MediaController:
    def __init__(self):
        self.plugins = []
        self.hub = Hub(self)
        self.__init_plugins()

    def __init_plugins(self):
        for section in conf.sections():
            if section != 'main':
                # Load plugins from config sections titles
                plugname = section.split('-')[0]
                try:
                    plugmodule = importlib.import_module(
                                'plugins.{}'.format(plugname)
                            )
                except ImportError:
                    logging.warning(
                        'Plugin {}, from config section [{}], '
                        'could not be loaded'.format(
                            plugname, section
                        )
                    )
                else:
                    plugclass = getattr(plugmodule, plugname.capitalize())
                    self.plugins.append(
                        plugclass(conf=conf, section=section,
                                  queue_to_hub=self.hub.inqueue)
                    )

    def run(self):
        self.__start_hub()
        self.__start_plugins()

    def __start_hub(self):
        self.hub.run()

    def __start_plugins(self):
        for plugin in self.plugins:
            plugin.run()



class Hub:
    def __init__(self, controller):
        self.controller = controller
        self.inqueue = queue.Queue()
        self.thread = threading.Thread(target=self.loop)

    def run(self):
        self.thread.start()
        logging.info('Started the hub')

    def loop(self):
        while True:
            msg = self.inqueue.get()
            if msg == 'stop':
                break
            logging.debug('New message on the bus: {}'.format(msg))
            self.__send_to_plugins(msg)

    def __send_to_plugins(self, msg):
        for plugin in self.controller.plugins:
            plugin.inqueue.put(msg)



def main():
    "Main loop"
    lvlname = conf.get('main', 'loglevel', fallback=DEFAULTS.loglevel).upper()
    logging.basicConfig(level=getattr(logging, lvlname))
    controller = MediaController()
    controller.run()

################################################################################
# Start the program

if len(sys.argv) > 1:
    configfile = sys.argv[1]
else:
    configfile = DEFAULTS.configfile
conf = configparser.ConfigParser()
conf.optionxform = str
conf.read_file(open(configfile))



if __name__ == '__main__':
    if conf.getboolean('main', 'daemon'):
        pidfile = conf.get('main', 'pidfile', fallback=DEFAULTS.pidfile)
        daemon = Daemonize(app="media-controller", pid=pidfile, action=main)
        daemon.start()
    else:
        main()