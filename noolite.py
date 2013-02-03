#!/usr/bin/python

# Requires: pyusb
# To install it on Ubuntu 12.04 do:
#   sudo apt-get install python-pip
#   sudo pip install pyusb

import os
import sys
import usb.core


class nooLite:
  def executeCommand(self, cmd, ch, lvl):
    command = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    command[1] = cmd
    command[4] = ch
    if cmd == 0x06:
      command[2] = 0x01
      command[5] = lvl
    dev = usb.core.find(idVendor=0x16c0, idProduct=0x05df)  # find NooLite PC118
    if dev is None:
      sys.exit('Device not found')
    if dev.is_kernel_driver_active(0) is True:
      dev.detach_kernel_driver(0)
    dev.set_configuration()
    dev.ctrl_transfer(0x21, 0x09, 0, 0, command)

class main:
  def usage(self, fileName):
    print 'Usage: ' + fileName + ' <cmdX> [level]'
    print 'Where:'
    print '  - <cmd> is:'
    print '      on_ch     - set channel X power ON'
    print '      off_ch    - set channel X power OFF'
    print '      sw_ch     - switch channel X power ON/OFF'
    print '      set_ch    - set channel X power level'
    print '      bind_ch   - bind channel X to device'
    print '      unbind_ch - unbind channel X from device'
    print '  - <X> is channel number from 1 to 8'
    print '  - [level] is power level for CMD "set_ch"'

  def execute(self, argv):
    if not os.geteuid() == 0:
      sys.exit("This script must be executed by root.")
    cmd = -1; ch = -1; lvl = 0;
    command = ''
    for arg in argv[1:]:
      if command == 'set_ch':
        if str(arg).isdigit():
          lvl = int(str(arg))
          if lvl<0:
            lvl=0
          elif lvl>100:
            lvl=100
          lvl = int(35 + 1.2 * lvl)
        break
      else:
        for sCmd, cCmd in [['on_ch', 0x02], ['off_ch', 0x00], ['sw_ch', 0x04], ['set_ch', 0x06], ['bind_ch', 0x0f], ['unbind_ch', 0x09]]:
          pos = str(arg).lower().find(sCmd)
          if pos >= 0:
            command = sCmd
            cmd = cCmd
            channel = str(arg[pos+len(sCmd):])
            if channel.isdigit():
              ch = int(channel)-1
            if ch<0 or ch>7:
              sys.exit('Channel number must be number from 1 to 8.')
            break
      if (len(command) > 0 and command != 'set_ch'):
        break
    if cmd>=0 and ch>=0:
      nooLite().executeCommand(cmd, ch, lvl)
    else:
      self.usage(argv[0])

if __name__ == '__main__':
  main().execute(sys.argv)
