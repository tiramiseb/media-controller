"""
Each configuration key is a button name from LIRC, and its
value is the message to send when pressing this button.
"""

# Default modules
import logging
import tempfile

# Dependencies
import lirc

# Local modules
from plugins import SenderPlugin, StopPlugin

################################################################################

class Irremote(SenderPlugin):
    def __init__(self, *args, **kwargs):
        SenderPlugin.__init__(self, *args, **kwargs)
        lircrc = tempfile.NamedTemporaryFile('w', delete=False)
        self.lircrc = lircrc.name
        for key, value in self.allconf():
            lircrc.write(
                'begin\n'
                '  prog = mediacontroller\n'
                '  button = {}\n'
                '  config = {}\n'
                'end\n'.format(key, value)
            )
        lircrc.close()

    def loop(self):
        try:
            sockid = lirc.init("mediacontroller", self.lircrc)
        except lirc.InitError:
            logging.error(
                'Failed to initialize LIRC, from section [{}]'.format(
                    self.section
                )
            )
            raise StopPlugin
        lirc.set_blocking(True, sockid)
        while True:
            self.send(lirc.nextcode())
