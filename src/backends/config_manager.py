# Module for configuration handling
#
#
# Copyright (c) 2003-2005 Erik Grinaker
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import gconf, os
from bd_exceptions.bubbledisk_exceptions import *



APPNAME		= "BubbledisK"
VERSION		= "0.0.1"
DATAVERSION	= 1
RELNAME		= "You are the operator of your disk generator"
URL		= "http://oss.codepoet.no/revelation/"
AUTHOR		= "Damien Solimando <dsolimando@it-optics.com>"
COPYRIGHT	= "Copyright \302\251 2005 DamieN SolimandO"

DIR_GCONFSCHEMAS= "/usr/share/gconf/schemas"
DIR_ICONS	= "/usr/share/icons"

FILE_GCONFTOOL	= "/usr/bin/gconftool-2"



class ConfigError(Exception):
	"Configuration error exception"
	pass



class Config(object):
	"Configuration class"

	basedir = ""
	client = None
	callbacks = []
	common_tools = None

	def __init__(self,common_tools, basedir = "/apps/bubbledisk"):
		self.common_tools = common_tools
		self.basedir	= basedir
		self.client	= gconf.client_get_default()
		self.callbacks	= {}

		# check config, install schema if needed
		if self.check() == False:
			if self.__install_schema(DIR_GCONFSCHEMAS + "/bubbledisk.schemas") == False or self.check() == False:
				raise ConfigError

		self.client.add_dir(self.basedir, gconf.CLIENT_PRELOAD_NONE)


	def __cb_notify(self, client, id, entry, data):
		"Callback for handling gconf notifications"

		value = entry.get_value()

		if value.type == gconf.VALUE_STRING:
			v = value.get_string()

		elif value.type == gconf.VALUE_BOOL:
			v = value.get_bool()

		elif value.type == gconf.VALUE_INT:
			v = value.get_int()


		# look up and call the callback
		if self.callbacks.has_key(id) == False:

			# workaround for 64-bit overflows in gnome-python (bug #170822)
			id += (2 ** 32)

			if self.callbacks.has_key(id) == False:
				raise ConfigError

		callback, userdata = self.callbacks[id]
		callback(entry.get_key(), v, userdata)


	def __install_schema(self, file):
		"Installs a gconf schema"

		if os.access(file, os.F_OK) == False:
			return False

		self.common_tools.execute(FILE_GCONFTOOL," --install-schema-file=" + file)


	def __resolve_keypath(self, key):
		"Resolves a key path"

		return key[0] == "/" and key or self.basedir + "/" + key


	def check(self):
		"Checks if the config is valid"

		try:
			self.get("writing/pregap")
			self.get("writing/addhiddenfiles")
			self.get("writing/addsystemfiles")
			self.get("writing/overburning")
			self.get("writing/eject")
			self.get("writing/blankcdrw")
			self.get("apps/path")
			self.get("misc/tempdir")
			self.get("misc/check_sysconfig")
			self.get("misc/hide_main_window")
			self.get("view/window_width")
			self.get("view/window_height")
			self.get("view/explorer_view")
			self.get("view/explorer_sense")

		except ConfigError:
			return False

		else:
			return True


	def forget(self, id):
		"Forgets a monitored key"

		if not self.callbacks.has_key(id):
			raise ConfigError

		self.client.notify_remove(id)
		del self.callbacks[id]


	def get(self, key):
		"Looks up a config value"

		value = self.client.get(self.__resolve_keypath(key))

		if value is None:
			raise ConfigError

		elif value.type == gconf.VALUE_STRING:
			return str(value.get_string())

		elif value.type == gconf.VALUE_INT:
			return value.get_int()

		elif value.type == gconf.VALUE_BOOL:
			return value.get_bool()

		elif value.type == gconf.VALUE_LIST:
			return value.get_list()


	def monitor(self, key, callback, userdata = None):
		"Monitor a config key for changes"

		key = self.__resolve_keypath(key)

		id = self.client.notify_add(key, self.__cb_notify)
		self.callbacks[id] = ( callback, userdata )

		# call the callback to set an initial state
		callback(key, self.get(key), userdata)

		return id


	def set(self, key, value):
		"Sets a configuration value"

		node = self.client.get(self.__resolve_keypath(key))

		if node is None:
			raise ConfigError

		elif node.type == gconf.VALUE_STRING:
			node.set_string(value)

		elif node.type == gconf.VALUE_BOOL:
			node.set_bool(value)

		elif node.type == gconf.VALUE_INT:
			node.set_int(int(value))

		elif node.type == gconf.VALUE_LIST:
			print type(value)
			node.set_list(gconf.VALUE_STRING,value)

		self.client.set(self.__resolve_keypath(key), node)

