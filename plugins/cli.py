# Default modules
import cmd
import readline
import time

# Local modules
from plugins import SenderPlugin

################################################################################

class Cli(SenderPlugin, cmd.Cmd):
    prompt = 'media-controller> '
    def __init__(self, *args, **kwargs):
        SenderPlugin.__init__(self, *args, **kwargs)
        cmd.Cmd.__init__(self)

    #######################################################
    # Stop the controller

    def do_stop(self, arg):
        "Stop the controller"
        return True

    def do_EOF(self, arg):
        "Stop the controller"
        print('')
        return True

    #######################################################
    # Send message

    def do_s(self, arg):
        "Send a message"
        self.send(arg)

    def do_send(self, arg):
        "Send a message"
        self.send(arg)

    def emptyline(self):
        pass

    #######################################################
    # The loop

    def loop(self):
        if self.configparser.getboolean('main', 'daemon'):
            logging.info('Not starting the CLI in daemon mode')
        else:
            self.cmdloop()

    def preloop(self):
        time.sleep(0.5)

    def postloop(self):
        self.send('stop')