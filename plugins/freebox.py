"""
Configuration keys:

* boxnumber: The number of the box (1 or 2)
* remotecode: The remotecode for this box

This plugin understands the following messages:

* freebox:remote:XXX where 'XXX' is a name of a Freebox remote key

Freebox remote key are:

* play
* rec
* bwd
* fwd
* prev
* next
* up
* down
* left
* right
* ok
* home
* prgm_inc
* prgm_dec
* 1
* 2
* 3
* 4
* 5
* 6
* 7
* 8
* 9
* 0
* red
* green
* yellow
* blue
"""

# Default modules
import logging
import urllib.error
import urllib.request

# Local modules
from plugins import ReceiverPlugin

################################################################################

class Freebox(ReceiverPlugin):
    messagefilters = ('freebox:')

    def __init__(self, *args, **kwargs):
        ReceiverPlugin.__init__(self, *args, **kwargs)

        self.url = ('http://hd{}.freebox.fr/pub/'
                    'remote_control?code={}&key={{}}').format(
            self.conf('boxnumber'),
            self.conf('remotecode')
        )
        print(self.url)

    def receive(self, msg):
        if msg.startswith('freebox:remote:'):
            self.remotesend(msg[15:])

    def remotesend(self, key):
        try:
            urllib.request.urlopen(self.url.format(key), timeout=1)
        except urllib.error.HTTPError:
            logging.warning('Could not send key to the Freebox '
                          '(probably wrong remote code)')
        except urllib.error.URLError:
            logging.warning('Could not send key to the Freebox '
                          '(probably unresponsive box)')