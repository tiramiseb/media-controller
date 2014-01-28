# Default modules
import cmd
import readline
import time

# Local modules
from plugins import SenderPlugin

################################################################################

#class MediaControllerShell(cmd.Cmd):
    #def __init__(self, *args, **kwargs):
        #cmd.Cmd.__init__(self, *args, **kwargs)

    #def do_EOF(self):


class Cli(SenderPlugin, cmd.Cmd):
    prompt = 'media-controller> '
    def __init__(self, *args, **kwargs):
        SenderPlugin.__init__(self, *args, **kwargs)
        cmd.Cmd.__init__(self)

    #######################################################
    # Stop the controller

    def do_stop(self, arg):
        return True

    def do_EOF(self, arg):
        print('')
        return True

    #######################################################
    # Send message

    def do_s(self, arg):
        self.send(arg)

    def do_send(self, arg):
        self.send(arg)

    def emptyline(self):
        pass

    #######################################################
    # The loop

    def loop(self):
        self.cmdloop()

    def preloop(self):
        time.sleep(0.5)

    def postloop(self):
        self.send('stop')