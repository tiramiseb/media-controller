# Default modules
import tempfile

# Dependencies
import lirc

# Local modules
from plugins import SenderPlugin

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
        sockid = lirc.init("mediacontroller", self.lircrc)
        lirc.set_blocking(True, sockid)
        while True:
            self.send(lirc.nextcode())