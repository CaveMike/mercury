#! /usr/bin/python
class TestListener(object):
	def onDefault( self, event ):
		print str(event)

class TestConfiguration(object):
	def __init__( self ):
		self.values = \
		{ \
			'network.localAddress'  : '127.0.0.1', \
			'network.localPort'     : 5060,        \
			'network.remoteAddress' : '127.0.0.1', \
			'network.remotePort'    : 5060,        \

			'test.timeout'          : 0.5,         \
		}

	def query( self, name, *args, **kwargs ):
		if not self.values.has_key( name ):
			return None

		return self.values[name]

