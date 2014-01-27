#!/usr/bin/env python3

# Default modules
import configparser
import importlib
import logging
import sys
import threading

# Dependencies
from daemonize import Daemonize
import zmq

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
        self.zmq_context = zmq.Context.instance()
        self.hub = Hub(self.zmq_context)
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
                                  zmq_context=self.zmq_context)
                    )

    def run(self):
        self.__start_hub()
        self.__start_plugins()

    def __start_plugins(self):
        for plugin in self.plugins:
            plugin.run()

    def __start_hub(self):
        self.hub.run()


class Hub:
    def __init__(self, zmq_context):
        self.insock = zmq.Context.instance().socket(zmq.SUB)
        self.outsock = zmq.Context.instance().socket(zmq.PUB)
        self.insock.setsockopt_string(zmq.SUBSCRIBE, '')
        self.insock.bind('inproc://fromplugin')
        self.outsock.bind('inproc://toplugin')
        self.thread = threading.Thread(target=self.loop)

    def run(self):
        self.thread.start()

    def loop(self):
        while True:
            self.outsock.send_string(self.insock.recv_string())


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
conf.read_file(open(configfile))



if __name__ == '__main__':
    if conf.getboolean('main', 'daemon'):
        pidfile = conf.get('main', 'pidfile', fallback=DEFAULTS.pidfile)
        daemon = Daemonize(app="media-controller", pid=pidfile, action=main)
        daemon.start()
    else:
        main()