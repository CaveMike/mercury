from node import *
from event import *

#-------------------------------------------------------------------------------
configuration = \
{
	# Network
	'network.maxmessage':     2048,
	'network.selecttimeout':  0.5,
	'network.connecttimeout': 4,
	'network.maxconnections': 10,
	'network.transport':      'udp',
	'network.localAddress':   '127.0.0.1',
	'network.localPort':      5060,
	'network.remoteAddress':  '127.0.0.1',
	'network.remotePort':     9001,
	'network.recvfromflags':  0,
	'network.sendtoflags':    0,
	'network.recvflags':      0,
	'network.sendflags':      0,
	'network.encoding':       'utf_8',

	# SIP
	'sip.timer.a':            4,
	'sip.timer.b':            4,
	'sip.timer.c':            4,
	'sip.timer.d':            4,
	'sip.timer.e':            4,
	'sip.timer.f':            4,
	'sip.timer.g':            4,
	'sip.timer.h':            4,
	'sip.timer.i':            4,
	'sip.timer.j':            4,
	'sip.timer.k':            4,
	'sip.useragent':          'SipBot',
}

#===============================================================================
class ConfigEvent(Event):
	EVENT_ACTIVE_CONFIG_CHANGED = 'ActiveConfigChanged'
	EVENT_SAVED_CONFIG_CHANGED  = 'SavedConfigChanged'

#===============================================================================
class Configuration(Node):

	EVENT_READ  = 'Read'
	EVENT_WRITE = 'Write'

	def onRead( self, event ):
		event.handled = True

	def onWrite( self, event ):
		event.handled = True

	def query( self, name, active = True, args = None, kwargs = None ):
		try:
			return configuration[name]
		except KeyError:
			# It is valid to get a query for a non-existent value.  For example, the state-timeouts often do not exist.
			return None
