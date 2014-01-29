"""
Configuration keys:

* squeezelitepath: The path to the squeezelite executable
* name: Name of the player

This plugin understands the following messages:

* squeezebox:start
* squeezebox:stop
"""

# Default modules
import logging
import subprocess

# Dependencies
import psutil

# Local modules
from plugins import Plugin

################################################################################

class Squeezebox(Plugin):

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.sqpath = self.conf('squeezelitepath')
        self.sqname = self.conf('name')

    def receive(self, msg):
        if msg == 'squeezebox:start':
            self.start()
        elif msg == 'squeezebox:stop':
            self.stop()

    def start(self):
        subprocess.call((
            self.sqpath,
            '-n',
            self.sqname,
            '-z'
        ))

    def stop(self):
        procname = self.sqpath.split('/')[-1]
        for proc in psutil.process_iter():
            if proc.name == procname:
                proc.kill()