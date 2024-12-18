# Copyright (c) 2024 by CrazyCat <crazycat@c-p-f.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------
# Adds alias with autocompletion for Anope
#
# ---------------------------------------------
# Think to change the chanserv setting in weechat
# Option name: plugins.var.tcl.anope.<network>.chanserv
# ---------------------------------------------
# History
# 2024-12-11 : Basic version: vop/hop/aop commands

set SCRIPT_VERSION 1.0
set SCRIPT_NAME anope
set SCRIPT_SUMMARY "Adds alias with autocompletion for Anope"

set CS_ARGS "vop|hop|aop <add|del> nick \[#channel\]"

set CS_ADESC "Alias for chanserv"

set CS_ACTIONS {"vop" "hop" "aop"}
::weechat::register $SCRIPT_NAME {CrazyCat <crazycat@c-p-f.org>} $SCRIPT_VERSION GPL3 $SCRIPT_SUMMARY {} {}
::weechat::hook_command cs $SCRIPT_SUMMARY $CS_ARGS $CS_ADESC {\
   vop add|del %(nicks) %(irc_server_channels)\
   || hop add|del %(nicks) %(irc_server_channels)\
   || aop add|del %(nicks) %(irc_server_channels)\
} cs_op {}

::weechat::hook_command global $SCRIPT_NAME "your global message here" "Send a message to all users" {} global_msg {}
array set SERVICES_NAMES {
   "chanserv"  "ChanServ"
   "nickserv"  "NickServ"
   "hostserv"  "HostServ"
   "global"    "Global"
}

array set SERVICES_DESC {
   "chanserv"  "Channel management service name"
   "nickserv"  "Channel management service name"
   "hostserv"  "Channel management service name"
   "global"    "Global messaging system"
}
proc anope_setup {} {
   set slist [::weechat::infolist_get "irc_server" "" ""]
   while {[::weechat::infolist_next $slist]} {
      set server [::weechat::infolist_string $slist "name"]
      foreach service [array names ::SERVICES_NAMES] {
         if {![::weechat::config_is_set_plugin "${server}.${service}"]} {
            ::weechat::config_set_plugin "${server}.${service}" $::SERVICES_NAMES($service)
            ::weechat::config_set_desc_plugin "${server}.${service}" $::SERVICES_DESC($service)
         }
      }
   }
   ::weechat::infolist_free $slist
}

proc global_msg {data buffer args} {
   lassign [buffer2sc $buffer] server schannel
   if {$server eq $::weechat::WEECHAT_RC_ERROR} {
      return $::weechat::WEECHAT_RC_ERROR
   }
   ::weechat::command "" "/msg [::weechat::config_get_plugin "${server}.global"] GLOBAL [join $args]"
   return $::weechat::WEECHAT_RC_OK
}

proc cs_op {data buffer args} {
   lassign [buffer2sc $buffer] server schannel
   if {$server eq $::weechat::WEECHAT_RC_ERROR} {
      return $::weechat::WEECHAT_RC_ERROR
   }
   lassign {*}$args csact csflag nick channel
   if {$csact ni $::CS_ACTIONS} {
      # bypass for unknown actions
      ::weechat::command "" "/msg [::weechat::config_get_plugin "${server}.chanserv"] [join $args]"
      return $::weechat::WEECHAT_RC_OK
   }
   if {$channel eq ""} {
      set channel $schannel
   }
   if {([string tolower $csflag] ni [list "add" "del"]) || ($nick eq "") || ($channel eq "")} {
      ::weechat::print $buffer "Usage: /cs $::CS_ARGS"
      return $::weechat::WEECHAT_RC_ERROR
   }
   ::weechat::command $server "/msg [::weechat::config_get_plugin "${server}.chanserv"] $csact $channel $csflag $nick"
   
   return $::weechat::WEECHAT_RC_OK
}

proc buffer2sc { buffer } {
   set btype [::weechat::buffer_get_string $buffer "localvar_type"]
   switch $btype {
      channel {
         set sc [split [::weechat::buffer_get_string $buffer "localvar_name"] {.}]
      }
      server {
         set sc [list [::weechat::buffer_get_string $buffer "localvar_channel"] ""]
      }
      default {
         ::weechat::print $buffer "Sorry but you need to be in a server or a channel to use this command"
         return $::weechat::WEECHAT_RC_ERROR
      }
   }
   return $sc
}

anope_setup
