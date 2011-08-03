#!/usr/bin/env python
from iron.dispatcher import Dispatcher
from iron.event import Event
from mercury.core import SipException
from mercury.header.header import SIP_CRLF
from mercury.message.message import Message
from mercury.message.message import MessageEvent
from mercury.message.message_assembler import DatagramReassembler
from mercury.message.message_assembler import StreamReassembler
from mercury.message.message_coder import MessageCoder
from mercury.network.netevent import NetError
from mercury.network.netevent import NetEvent
from mercury.network.network import Network
import logging

class MessageAdapter(object):
	"""Adapts between NetEvents and MessageEvents.
	   Routes outgoing MessageEvents to the appropriate destination using the
	   the appropriate source.
	"""
	def __init__( self, name, parent ):
		#super( MessageAdapter, self ).__init__( name, parent )
		self.log = logging.getLogger( self.__class__.__name__ )

		self.network = Network( 'net', self )
		self.network.addListener( self )

		self.coder = MessageCoder( self.query( 'network.encoding' ) )

		self.default = DatagramReassembler()
		self.connections = {}

	def identifyEvent( self, event ):
		self.log.info( str(event) )

		if isinstance( event, MessageEvent ):
			return event.id
		elif isinstance( event, NetEvent ):
			return event.id
		elif isinstance( event, NetError ):
			return event.id

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	def onBind( self, event ):
		# Pass through to the underlying network implementation.
		self.send( event, self.network, queued=False )

	def onUnbind( self, event ):
		# Pass through to the underlying network implementation.
		self.send( event, self.network, queued=False )

	def onRxPacket( self, event ):
		# Decode the message and, if the decoding succeeded, pass the MessageEvent up.
		text = self.coder.decode( event.packet )

		if not event.connection:
			message = self.default.parse( text )
		else:
			#FIXME: handle KeyError.
			message = self.connections[event.connection].parse( text )

		if message != None:
			newEvent = MessageEvent( MessageEvent.EVENT_RX, message, transport=event.transport, localAddress=event.localAddress, localPort=event.localPort, remoteAddress=event.remoteAddress, remotePort=event.remotePort, useragent=self )
			self.notify( newEvent, queued=False )

		event.handled = True

	def __onTxPacket( self, event ):
		# Determine the transport, addresses, and ports to use and adjust the
		# SIP message as necessary.
		self.routeMessage( event )

		# Encode the message, and if the encoding succeeded, pass the NetEvent down.
		text = self.coder.encode( event.message )
		newEvent = NetEvent( NetEvent.EVENT_TX_PACKET, event.transport, event.localAddress, event.localPort, event.remoteAddress, event.remotePort, packet=text )

		if newEvent:
			self.send( newEvent, self.network, queued=False )

		event.handled = True

	def onTxRequest( self, event ):
		self.__onTxPacket( event )

	def onTxResponse( self, event ):
		self.__onTxPacket( event )

	def onConnected( self, event ):
		print 'ccc', str(event.connection)
		self.connections[event.connection] = StreamReassembler()
		event.handled = True

	def onDisconnected( self, event ):
		#FIXME: handle KeyError.
		print 'ddd', str(event.connection)
		#print self.connections
		del self.connections[event.connection]
		event.handled = True

	def onNetError( self, event ):
		self.log.error( str(event) )

		#FIXME: Not sure what to do with these events.  Should they be sent up as-is?
		#       Or converted to MessageEvents?
		self.notify( event, queued=False )

		event.handled = True

	def routeMessage( self, event ):
		"""This function determines the address and port to send the message to.
		   For requests, this function also determines the transport, address, and port to
		   send the message from.

		   Request:
		      Look up Request-URI host and get remote transport, address and port.
		      Modify/set Contact.
		      Modify/set Via to local transport, address, and port.

		   Response:
		      Get the destination from the Via.
		"""

		#FIXME:IMPLEMENT.
		pass

