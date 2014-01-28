"""
Configuration keys:

* irsend: path to the irsend command
* device: path to the LIRC device (/var/run/lirc/...)
* remotename: name of the remote in /etc/lirc/lircd.conf
* (optional) statusfile: file where to store the status

This plugin understands the following messages:

* sound:vol+
* sound:vol-
* sound:mute
* z680:input direct
* z680:input optical
* z680:input coax
* z680:power on
* z680:power off

The lines in /etc/lirclircd.conf should be:
begin remote
  name  LogitechZ680
  bits           16
  flags SPACE_ENC|CONST_LENGTH
  eps            30
  aeps          100
  header       9041  4412
  one           604  1620
  zero          604   494
  ptrail        610
  repeat       9042  2174
  pre_data_bits   16
  pre_data       0x10EF
  gap          107692
  toggle_bit_mask 0x0
      begin codes
          test                     0xA05F
          power                    0x08F7
          input                    0x906F
          effect                   0xB847
          settings                 0xF807
          sub+                     0xC03F
          sub-                     0x807F
          center+                  0x40BF
          center-                  0x609F
          surround+                0x00FF
          surround-                0x20DF
          mute                     0x6897
          +                        0x58A7
          -                        0x708F
      end codes
end remote
"""

# Default modules
import logging
import subprocess
import time

# Local modules
from plugins import ReceiverPlugin, StopPlugin

try:
   filenotfoundexception = FileNotFoundError
except NameError:
   filenotfoundexception = IOError

################################################################################

class DEFAULTS:
    statusfile = 'logitech_z680.status'
    wait_between_impulses = 0.25

translation_table = {
    'sound:vol+': '+',
    'sound:vol-': '-',
    'sound:mute': 'mute'
}

inputs = ['direct', 'optical', 'coax']

################################################################################

class Logitechz680(ReceiverPlugin):
    messagefilters = ('sound', 'z680')

    def __init__(self, *args, **kwargs):
        ReceiverPlugin.__init__(self, *args, **kwargs)
        self.lirc_irsend = self.conf('irsend')
        self.lirc_device = self.conf('device')
        self.lirc_remotename = self.conf('remotename')
        self.__read_status()

    def __read_status(self):
        try:
            statusfile = open(self.conf('statusfile', DEFAULTS.statusfile), 'r')
        except filenotfoundexception:
            self.current_input = inputs[0]
            self.current_power = False
            return
        for l in statusfile:
            conf = l.split('=')
            if len(conf) == 2:
                confname = conf[0].strip()
                confvalue = conf[1].strip()
                if confname == 'input':
                    self.current_input = confvalue
                elif confname == 'power':
                    self.current_power = confvalue == 'on'

    def __write_status(self):
        with open(self.conf('statusfile', DEFAULTS.statusfile), 'w') as f:
            f.write(
                'input={}\npower={}'.format(
                    self.current_input,
                    self.current_power and 'on' or 'off'
                )
            )

    def power(self, onoff=True):
        if onoff != self.current_power:
            self.irsend('power')
            self.current_power = onoff
            self.__write_status()

    def switch_to_input(self, name):
        if name in inputs:
            self.power()
            nb_impulses = inputs.index(name) - inputs.index(self.current_input)
            if nb_impulses < 0:
                nb_impulses = len(inputs) - nb_impulses
            for i in range(nb_impulses):
                self.irsend('input')
            self.curent_input = name
            self.__write_status()

    def irsend(self, code):
        try:
            subprocess.call((
                self.lirc_irsend,
                '-d',
                self.lirc_device,
                'SEND_ONCE',
                self.lirc_remotename,
                code
            ))
            time.sleep(DEFAULTS.wait_between_impulses)
        except FileNotFoundError:
            self.error(
                'The defined irsend command ({}) does '
                'not exist'.format(self.conf('irsend'))
            )

    def receive(self, msg):
        if msg in translation_table:
            self.irsend(translation_table[msg])
        elif msg.startswith('z680:input'):
            self.switch_to_input(msg[11:])
        elif msg.startswith('z680:power'):
            self.power(msg[11:] == 'on')