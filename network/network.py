#!/usr/bin/env python
from iron.dispatcher import Dispatcher
from mercury.network.netevent import NetEvent
from mercury.network.netevent import NetError
from errno import errorcode
from iron.event import Event
from carbon.importer import importExtension
from Queue import Queue
from select import select
from socket import AF_INET
from socket import error
from socket import SHUT_RDWR
from socket import SO_ERROR
from socket import SO_REUSEADDR
from socket import SOCK_DGRAM
from socket import SOCK_STREAM
from socket import socket
from socket import SOL_SOCKET
from threading import Thread
from time import sleep
from iron.context import Context
from iron.state import StateEvent
import logging

class Network(object):
	# NetEvent
	# NetError

	DEFAULT_CONFIGURATION = \
	{ \
		# Socket
		'network.selecttimeout' : 0.5,  \

		# General
		'network.maxmessage'    : 2048, \

		# UDP
		'network.recvfromflags' : 0,    \
		'network.sendtoflags'   : 0,    \

		# TCP
		'network.connecttimeout' : 5,  \
		'network.maxconnections' : 10, \
		'network.recvflags'      : 0,  \
		'network.sendflags'      : 0,  \
	}

	def __init__( self ):
		super( Network, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )

		self.bindings = {}
		self.__thread = None

		self.config = None

	@staticmethod
	def getBindingName( transport, localAddress, localPort ):
		return '%s:%s:%s' % ( transport, localAddress, localPort )

	def addConfiguration( self, config ):
		self.config = config

	def query( self, name, *args, **kwargs ):
		value = None

		if self.config:
			value = self.config.query( name, args, kwargs )

		if value is None:
			value = self.DEFAULT_CONFIGURATION[name]

		return value

	def identifyEvent( self, event ):
		self.log.info( str(event) )
		if isinstance( event, NetEvent ):
			return event()
		elif isinstance( event, NetError ):
			return event()
		elif isinstance( event, StateEvent ):
			return event.state

		raise Exception( 'Ignoring event ' + str(event) + '.' )

	def onBind( self, event ):
		name = str(event.transport) + ':' + str(event.localAddress) + ':' + str(event.localPort)
		binding = Binding( event )
		Dispatcher.add( binding, parentObj=self )
		Dispatcher.addListener( binding, self )

		name = Network.getBindingName( event.transport, event.localAddress, event.localPort )
		self.bindings[name] = binding

		Dispatcher.send( event, srcObj=self, dstObj=binding )

		if not self.__thread:
			self.__thread = Thread( None, self.run )
			self.__thread.start()

	def onUnbind( self, event ):
		name = Network.getBindingName( event.transport, event.localAddress, event.localPort )
		binding = self.bindings[name]
		if binding:
			Dispatcher.send( event, srcObj=self, dstObj=binding )
			del self.bindings[ name ]

	def onRxPacket( self, event ):
		Dispatcher.notify( event )

	def onTxPacket( self, event ):
		event.id = BindingBase.EVENT_QUEUE

		name = Network.getBindingName( event.transport, event.localAddress, event.localPort )
		binding = self.bindings[name]
		if binding:
			Dispatcher.send( event, srcObj=self, dstObj=binding )
		else:
			for binding in self.bindings.itervalues():
				result = Dispatcher.send( event, srcObj=self, dstObj=binding )
				if result:
					break

	def onConnected( self, event ):
		Dispatcher.notify( event )

	def onDisconnected( self, event ):
		Dispatcher.notify( event )

	def onNetError( self, event ):
		Dispatcher.notify( event )

	def onBound( self, event ):
		pass

	def onUnbound( self, event ):
		pass

	def run( self ):
		while True:
			timeout = self.query( 'network.selecttimeout' )

			readSet = set()
			writeSet = set()
			errorSet = set()
			#FIXME: There needs to be locking here since a socket can
			#       be killed while we are enumerating.
			for binding in self.bindings.itervalues():
				binding.getReadyBindings( readSet, writeSet, errorSet )

			read = [ binding for binding in readSet ]
			write = [ binding for binding in writeSet ]
			error = [ binding for binding in errorSet ]

			if len(errorSet) or len(readSet) or len(writeSet):
				read, write, error = select( read, write, error, timeout )

 				for binding in read:
 					event = Event( binding.EVENT_READ )
					Dispatcher.send( event, srcObj=self, dstObj=binding )

 				for binding in write:
 					event = Event( binding.EVENT_WRITE )
					Dispatcher.send( event, srcObj=self, dstObj=binding )

 				for binding in error:
 					event = Event( binding.EVENT_ERROR )
					Dispatcher.send( event, srcObj=self, dstObj=binding )
			else:
				sleep( timeout )

class Binding(type):
	def __new__( cls, event ):
		if cls == Binding:
			obj = importExtension( event.transport + '_binding' )

			if obj:
				return obj( event )

			raise Exception( 'Cannot create binding, ' + str(event.transport) + '.' )
		else:
			# Just build the object.
			return type.__new__( cls, event )

class BindingBase(object):
	STATE_INITIAL   = 'Initial'
	STATE_BINDING   = 'Binding'
	STATE_BOUND     = 'Bound'
	STATE_UNBINDING = 'Unbinding'
	STATE_UNBOUND   = 'Unbound'

	# Socket events not used outside of the network modules.
	EVENT_QUEUE   = 'Queue'
	EVENT_READ    = 'Read'
	EVENT_WRITE   = 'Write'
	EVENT_ERROR   = 'Error'

import unittest
from test_helpers import TestListener
from test_helpers import TestConfiguration

class TestNetwork(unittest.TestCase):
	def runTest( self ):
		c = Context( 'Root' )
		c.start()

		l = TestListener()
		Dispatcher.add( l, context=c )

		config = TestConfiguration()

		o = Network()
		Dispatcher.add( o, context=c )
		Dispatcher.addListener( o, l )
		o.addConfiguration( config )

		e = NetEvent( NetEvent.EVENT_BIND, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ) )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		packet = '' \
'REGISTER sip:sip.example.com SIP/2.0\r\n' \
'Via: SIP/2.0/UDP 192.168.1.1:5060;rport;branch=z9hG4bK58790139-438475846\r\n' \
'Max-Forwards: 70\r\n' \
'Allow: INVITE,BYE,CANCEL,ACK,INFO,PRACK,OPTIONS,SUBSCRIBE,NOTIFY,PUBLISH,MESSAGE,REFER,REGISTER,UPDATE\r\n' \
'Supported: path,replaces,norefersub\r\n' \
'User-Agent: IMS Phone 49\r\n' \
'From: <sip:1@sip.example.com>;tag=UA_58790139-438475847\r\n' \
'To: <sip:1@sip.example.com>\r\n' \
'Call-ID: 58790139-438475845\r\n' \
'CSeq: 1 REGISTER\r\n' \
'Expires: 3600\r\n' \
'Contact: 1<sip:1@192.168.1.1:5060;transport=udp>;expires=3600\r\n' \
'Authorization: Digest username="1",realm="sip.example.com",nonce="",uri="sip:sip.example.com",response=""\r\n' \
'Content-Length: 0\r\n' \
'\r\n'

		e = NetEvent( NetEvent.EVENT_TX_PACKET, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ), remoteAddress=config.query( 'network.remoteAddress' ), remotePort=config.query( 'network.remotePort' ), packet=packet )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		e = NetEvent( NetEvent.EVENT_UNBIND, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ) )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		c.stop( config.query( 'test.timeout' ) )

if __name__ == "__main__":
	import logging

	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main( exit=True, verbosity=2 )

