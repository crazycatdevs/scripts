#
# Copyright (c) 2007 by pr3d4t0r (tek_fox AT internet.lu)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# pmwhitelist.py -- GPLv2
#
# Private messages white list for WeeChat 0.2.x.
# This script implements the commands /whitelist or
# /wl for managing users into a white list.  The WeeChat user will only
# receive private messages from white listed users.  All others will 
# receive an automatic response indicating that the message didn't reach
# the WeeChat user and instructions to make an in-channel request 
# to be added to the white list.
#
# /whitelist and /wl can be used in combination with these actions:
#
# /whitelist add nick
# /whitelist del nick
# /whitelist view
#
# The script can be loaded into WeeChat by executing:
#
# /python load pmwhitelist.py
#
# The script may also be auto-loaded by WeeChat.  See the
# WeeChat manual for instructions about how to do this.
#
# This script was tested with WeeChat versions 0.2.4 and
# 0.2.6.  An updated version of this script will be available
# when the new WeeChat API is released.
#
# For up-to-date information about this script, and new
# version downloads, please go to:
#
# http://eugeneciurana.com/site.php?page=tools
#
# If you have any questions, please contact me on-line at:
#
# irc.freenode.net - pr3d4t0r (op):  ##java, #awk, #esb
# irc.freenode.net - pr3d4t0r (op):  #java
# irc.osx86.hu     - pr3d4t0r (op):  #iphone-dev
#
# The fastest way to make feature requests or report a bug:
#
# http://eugeneciurana.com/site.php?page=contact
#
# Cheers!
#
# pr3d4t0r
#
# CHANGE LOG
# ==========
# 0.2 fixed:  ~/.weechat/white_list.dat not found error
# 0.3 fixed:  No more endless looping if sender and recipient both have pmwhitelist.py
#             installed, or if the recipient is a 'bot not in the white list.
# 0.4 added:  Notification to the current network server console that a user tried
#             to send a private message, and who that user was.  Also, fixed the
#             mechanism for clearing the '\n' at the end of each line read from the
#             white list.
# 0.5 fixed:  Bug in auto-reply; the first time that a user sends a message, she gets the
#             auto-reply; the second time she's able to send private messages.
#
#             Removed:  help command.
# 0.6 added:  Updated the /wl add method to allow the user to enter multiple nicks
#             in one operation:  /wl add bob bob- alice alice_


import        os
import        string
import        weechat


# *** Symbolic constants ***

FILE_NAME     = "white_list.dat"

COMMANDS      = [ "add", "del", "view" ]


# *** Globals ***

greyList      = []


# *** Implementation and callback functions ***

def end_PMWhiteList():
  weechat.prnt("PMWhiteList: ending...")
  
  return weechat.PLUGIN_RC_OK
# end_PMWhiteList


def killPrivateMessage(bufferSender, bufferHome, myNick, bAutoReply):
  weechat.command("/buffer "+bufferSender)

  if (True == bAutoReply):
    weechat.command("/say AUTOREPLY:  "+myNick+" does not accept unsolicited private messages.  Your message didn't reach the recipient.  Please ask for your nick to be white listed in-channel.  Thank you.")
    
  weechat.command("/close")
  weechat.command("/buffer "+bufferHome)
# killPrivateMessage


def whiteListFileName():
  return weechat.get_info("weechat_dir")+"/"+FILE_NAME;
# whiteListFileName


def  readList():
  whiteList = []  # init
  if os.access(whiteListFileName(), os.F_OK) == False:
    outputFile = open(whiteListFileName(), "wb")
    outputFile.writelines(whiteList)
    outputFile.close()

  inputFile = open(whiteListFileName(), "rb")
  list      = inputFile.readlines()
  inputFile.close()

  for item in list:
    whiteList.append(item.rstrip('\n'))

  whiteList.sort()
  return whiteList
# readList


def writeList(whiteList):
  outputFile = open(whiteListFileName(), "wb")
  outputFile.writelines(whiteList)
  outputFile.close()
# writeList


def isOnList(nickSender):
  whiteList = readList()

  for nick in whiteList:
    if (nickSender.lower() == nick.lower()):
      return True

  return False
# isOnList


def whiteListAdd(nickList):
  if nickList == None or len(nickList) < 1:
    return

  list     = readList()

  for nick in nickList:
    weechat.print_server("Private message white list add: "+nick)
    if nick not in list:
      list.append(nick)

    if nick in greyList:
      greyList.remove(nick)

  whiteList = []
  for item in list:
    whiteList.append(item+"\n")

  writeList(whiteList)
# whiteListAdd


def whiteListDel(nick):
  weechat.print_server("Private message white list delete: "+nick)
  list      = readList()
  whiteList = []
  for item in list:
    if item != nick:
      whiteList.append(item+"\n")

  writeList(whiteList)
# whiteListDel


def whiteListDisplay():
  weechat.print_server("*** Begin private message white list:")
  for nick in readList():
    weechat.print_server(nick)

  weechat.print_server("*** End private message white list\n")
# whiteListDisplay


def PMWLInterceptor(server, argList):
  bufferSender = argList.split(":")[1].split(" ")[0].split("!")[0]
  nickSender   = bufferSender
  bufferHome   = weechat.get_info("channel", server)
  myNick       = weechat.get_info("nick", server)

  if os.access(whiteListFileName(), os.F_OK) == False:
    killPrivateMessage(bufferSender, bufferHome, myNick, True)
    return weechat.PLUGIN_RC_OK

  if (False == isOnList(nickSender)):
    if (nickSender not in greyList):
      killPrivateMessage(bufferSender, bufferHome, myNick, True)
      greyList.append(nickSender)
      weechat.print_server(nickSender+" tried to send a private message.")
    else:
      killPrivateMessage(bufferSender, bufferHome, myNick, False)

  return weechat.PLUGIN_RC_OK
# PMWLInterceptor


def PMWLCommandHandler(server, argList):
  command = argList.split(" ")[0]

  if command not in COMMANDS:
    return weechat.PLUGIN_RC_KO

  if len(argList.split(" ")) <= 1:
    arguments = list() 
  else:
    arguments = argList.split(" ")[1:]

  if (command.lower() == "view"):
    whiteListDisplay()
    return weechat.PLUGIN_RC_OK

  if (len(arguments) < 1):
    return weechat.PLUGIN_RC_KO

  if (command.lower() == "add"):
    whiteListAdd(arguments)

  if (command.lower() == "del"):
    whiteListDel(arguments[0])

  return weechat.PLUGIN_RC_OK
# PMWLCommandHandler


# *** Script starts here ***

weechat.register("PMWhiteList", "0.6", "end_PMWhiteList", "Private messages white list", "UTF-8");
weechat.set_charset("UTF-8");
weechat.add_message_handler("weechat_pv", "PMWLInterceptor")
weechat.add_command_handler("whitelist", "PMWLCommandHandler", "Private message white list", "add|del|view", "add nick1 nick2 ... nickN, delete nick, or view white list", "add|del|view")
weechat.add_command_handler("wl", "PMWLCommandHandler", "Private message white list (shorthand for /whitelist)", "add|del|view", "add nick1 nick2 ... nickN, delete nick, or view white list", "add|del|view")
