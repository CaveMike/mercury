#! /usr/bin/python
from iron.event import Event
from time import time

class NetEvent(Event):
	EVENT_BIND         = 'Bind'
	EVENT_UNBIND       = 'Unbind'
	EVENT_CONNECTED    = 'Connected'
	EVENT_DISCONNECTED = 'Disconnected'
	EVENT_RX_PACKET    = 'RxPacket'
	EVENT_TX_PACKET    = 'TxPacket'

	def __init__( self, id, transport, localAddress, localPort, remoteAddress = None, remotePort = None, packet = None, binding = None, connection = None ):
		super( NetEvent, self ).__init__( id )

		self.transport = transport
		self.localAddress = localAddress
		self.localPort = localPort
		self.remoteAddress = remoteAddress
		self.remotePort = remotePort

		self.packet = packet

		self.binding = binding
		self.connection = connection

		self.timestamp = time()

	def __str__( self ):
		l = 0
		if self.packet:
			l = len(self.packet)
		return '%s, %s(%s:%s %s:%s), packetLength: %s, timestamp: %s' % ( Event.__str__(self), str(self.transport), str(self.localAddress), str(self.localPort), str(self.remoteAddress), str(self.remotePort), str(l), str(self.timestamp) )

class NetError(Event):
	NOTIFICATION_TRANSPORT_ERROR = 'NetError'

	def __init__( self, code, description, transport, localAddress, localPort, remoteAddress = None, remotePort = None, binding = None, connection = None ):
		super( NetError, self ).__init__( self.NOTIFICATION_TRANSPORT_ERROR )

		if not description:
			if errorcode.has_key( code ):
				description = errorcode[code]

		self.code = code
		self.description = description

		self.transport = transport
		self.localAddress = localAddress
		self.localPort = localPort
		self.remoteAddress = remoteAddress
		self.remotePort = remotePort

		self.binding = binding
		self.connection = connection

	def __str__( self ):
		return '%s, code: %s, description: %s, %s(%s:%s %s:%s)' % (  Event.__str__(self), str(self.code), str(self.description), str(self.transport), str(self.localAddress), str(self.localPort), str(self.remoteAddress), str(self.remotePort) )

