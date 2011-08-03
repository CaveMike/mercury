#! /usr/bin/python
from iron.delegator import Delegator
from iron.dispatcher import Dispatcher
from mercury.network.network import BindingBase
from mercury.network.network import NetError
from mercury.network.network import NetEvent
from mercury.network.network import Network
from Queue import Queue
from select import select
from socket import AF_INET
from socket import error
from socket import SHUT_RDWR
from socket import SO_ERROR
from socket import SO_REUSEADDR
from socket import SOCK_STREAM
from socket import socket
from socket import SOL_SOCKET
from iron.state import StateEvent
from iron.state import State
from time import time
import logging

#===============================================================================
class TcpBinding(BindingBase):
	DEFAULT_CONFIGURATION = \
	{ \
		'network.maxmessage'    : 2048, \

		'network.connecttimeout' : 5,  \
		'network.maxconnections' : 10, \
		'network.recvflags'      : 0,  \
		'network.sendflags'      : 0,  \
	}

	def __init__( self, event ):
		super( TcpBinding, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )

		self.transport = event.transport
		self.localAddress = event.localAddress
		self.localPort = event.localPort

		self.socket = None
		self.connections = {}

		self.state = self.STATE_INITIAL
		self.config = None

	def addConfiguration( self, config ):
		self.config = config

	def query( self, name, *args, **kwargs ):
		value = None

		if self.config:
			value = self.config.query( name, args, kwargs )

		if value is None:
			value = self.DEFAULT_CONFIGURATION[name]

		return value

	def identifyState( self, event ):
		return self.state

	def fileno( self ):
		if self.socket:
			fileno = self.socket.fileno()
			if fileno == -1:
				raise Exception( 'The binding socket has been closed.  It is likely that select() is trying to use this binding, but the binding is not ready.' )
			else:
				return fileno
		else:
			raise Exception( 'Binding does not have a socket.  It is likely that select() is trying to use this binding, but the binding is not ready.' )

	def getReadyBindings( self, read, write, error ):
		if self.readyToRead():
			read.add( self )

		if self.readyToWrite():
			write.add( self )

		if self.readyToError():
			error.add( self )

		for connection in self.connections.itervalues():
			connection.getReadyBindings( read, write, error )

	def readyToRead( self ):
		return self.socket and self.currentState == self.STATE_BOUND

	def readyToWrite( self ):
		return False

	def readyToError( self ):
		return self.socket and self.currentState != self.STATE_UNBINDING and self.currentState != self.STATE_UNBOUND

	# Initial
	def inInitial_onBind( self, event ):
		self.state = self.STATE_BINDING
		#Dispatcher.notify( StateEvent( State.EVENT_STATE_CHANGE, self.state, self.STATE_INITIAL ) )

		self.socket = socket( AF_INET, SOCK_STREAM )
		self.socket.setblocking( 0 )
		self.socket.bind( ( self.localAddress, self.localPort ) )
		self.socket.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )
		self.socket.listen( self.query( 'network.maxconnections' ) )

		event.binding = self
		self.state = self.STATE_BOUND
		Dispatcher.notify( StateEvent( State.EVENT_STATE_CHANGE, self.state, self.STATE_INITIAL ) )

	# Bound
	def inBound_onQueue( self, event ):
		if not event.connection:
			if ( event.localAddress != self.localAddress ) or ( event.localPort != self.localPort ):
				# This is not our binding.
				return

			# Let the network layer choose the local port.
			event.localPort = 0

			# Create a new connection and queue the event in the connection.
			connection = TcpConnection( event.transport, event.localAddress, event.localPort, event.remoteAddress, event.remotePort )
			Dispatcher.add( connection, parentObj=self )
			Dispatcher.addListener( connection, self )

			name = Network.getBindingName( connection.transport, connection.remoteAddress, connection.remotePort )
			self.connections[name] = connection

		Dispatcher.send( event, srcObj=self, dstObj=connection )

	def inBound_onRead( self, event ):
		self.accept()

	def inBound_onError( self, event ):
		error = self.socket.getsockopt( SOL_SOCKET, SO_ERROR )
		Dispatcher.notify( NetError( error, None, self.transport, self.localAddress, self.localPort ) )

		self.close( event )

	def inBound_onUnbind( self, event ):
		self.close( event )

	def inBound_onConnected( self, event ):
		Dispatcher.notify( event )

	def inBound_onDisconnected( self, event ):
		Dispatcher.notify( event )

	# Unbound

	# Default
	def onRxPacket( self, event ):
		Dispatcher.notify( event )

	# Helpers
	def accept( self ):
		if self.socket:
			(newSocket, remote) = self.socket.accept()

			connection = TcpConnection( self.transport, self.localAddress, self.localPort, remoteAddress=remote[0], remotePort=remote[1], csocket=newSocket )
			Dispatcher.add( connection, parentObj=self )
			Dispatcher.addListener( connection, self )

			name = Network.getBindingName( connection.transport, connection.remoteAddress, connection.remotePort )
			self.connections[name] = connection

			# Send the TCP connection's connected notification to ourselves.
			# This is a work-around, since we are constructing the connection in the connected state and
			# we do not want to send the event in the TCP connection's constructor.
			newEvent = NetEvent( NetEvent.EVENT_CONNECTED, connection.transport, connection.localAddress, connection.localPort, connection.remoteAddress, connection.remotePort, connection=connection )
			Dispatcher.send( newEvent, srcObj=self, dstObj=self )

	def close( self, event ):
		self.state = self.STATE_UNBINDING

		self.socket.close()
		self.socket = None

		event.binding = self
		self.state = self.STATE_UNBOUND, event.id, event
		Dispatcher.notify( StateEvent( State.EVENT_STATE_CHANGE, self.state, self.STATE_BOUND ) )

#===============================================================================
class TcpConnection(BindingBase):
	STATE_CONNECTING         = 'Connecting'
	STATE_CONNECTED          = 'Connected'
	STATE_DISCONNECTING      = 'Disconnecting'
	STATE_DISCONNECTED       = 'Disconnected'
	#STATE_ERROR              = 'Error'

	def __init__( self, transport, localAddress, localPort, remoteAddress, remotePort, csocket = None ):
		super( TcpConnection, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )

		self.transport = transport
		self.localAddress = localAddress
		self.localPort = localPort
		self.remoteAddress = remoteAddress
		self.remotePort = remotePort

		self.socket = csocket
		self.__queue = Queue()

		self.state = self.STATE_INITIAL
		self.config = None

		if self.socket:
			self.state = self.STATE_CONNECTED
		else:
			self.socket = socket( AF_INET, SOCK_STREAM )
			self.socket.setblocking( 0 )
			self.socket.bind( ( self.localAddress, self.localPort ) )
			self.socket.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )
			self.state = self.STATE_BOUND

	def __str__( self ):
		return 'name: %s %s(%s:%s %s:%s) q:%s' % ( str(self.name), str(self.transport), str(self.localAddress), str(self.localPort), str(self.remoteAddress), str(self.remotePort), str(len(self.__queue)) )

	def identifyState( self, event ):
		return self.state

	def fileno( self ):
		if self.socket:
			fileno = self.socket.fileno()
			if fileno == -1:
				raise Exception( 'The binding socket has been closed.  It is likely that select() is trying to use this binding, but the binding is not ready.' )
			else:
				return fileno
		else:
			raise Exception( 'Binding does not have a socket.  It is likely that select() is trying to use this binding, but the binding is not ready.' )

	def getReadyBindings( self, read, write, error ):
		if self.readyToRead():
			read.add( self )

		if self.readyToWrite():
			write.add( self )

		if self.readyToError():
			error.add( self )

	def readyToRead( self ):
		return self.socket and self.currentState == self.STATE_CONNECTED

	def readyToWrite( self ):
		if self.socket:
			if self.currentState == self.STATE_CONNECTING:
				return True
			elif self.currentState == self.STATE_CONNECTED:
				return not self.__queue.empty()
		return False

	def readyToError( self ):
		return self.socket and self.currentState != self.STATE_DISCONNECTING and self.currentState != self.STATE_DISCONNECTED

	# Initial
	def inInitial_onBind( self, event ):
		pass

	# Bound
	def inBound_onQueue( self, event ):
		self.__queue.put( event )

		self.remoteAddress = event.remoteAddress
		self.remotePort = event.remotePort
#FIXME:		self.socket.settimeout( self.query( 'network.connecttimeout' ) )
		try:
			self.socket.connect( (event.remoteAddress, event.remotePort) )

			self.state = self.STATE_CONNECTING

			return True
		except error, e:
			newEvent = NetError( e[0], e[1], self.transport, self.localAddress, self.localPort, connection=self )
			Dispatcher.notify( newEvent )

			self.close( event )

			return False

	# Connecting
	def inConnecting_onWrite( self, event ):
		self.state = self.STATE_CONNECTED

	def inConnecting_onError( self, event ):
		error = self.socket.getsockopt( SOL_SOCKET, SO_ERROR )
		Dispatcher.notify( NetError( error, None, self.transport, self.localAddress, self.localPort, self.remoteAddress, self.remotePort, connection=self ) )

		self.close( event )

	# Connected
	def inConnected_onRead( self, event ):
		if self.socket:
			buffer = self.socket.recv( self.query( 'network.maxmessage' ), self.query( 'network.recvflags' ) )
			if buffer:
				self.log.info( 'recv:\n%s(%s:%s %s:%s)\n%s.' % ( str(self.transport), str(self.localAddress), str(self.localPort), str(self.remoteAddress), str(self.remotePort), str(buffer) ) )

				newEvent = NetEvent( NetEvent.EVENT_RX_PACKET, self.transport, self.localAddress, self.localPort, self.remoteAddress, self.remotePort, packet=str(buffer), connection=self )
				Dispatcher.notify( newEvent )
			else:
				# Remote disconnect.
				self.close( event )

	def inConnected_onWrite( self, event ):
		if not self.__queue.empty():
			newEvent = self.__queue.get()

			bytes = self.socket.send( str(newEvent.packet), self.query( 'network.sendflags' ) )
			self.log.info( 'send:\n%s(%s:%s %s:%s)\n%s.' % ( str(self.transport), str(self.localAddress), str(self.localPort), str(self.remoteAddress), str(self.remotePort), str(newEvent.packet) ) )

			event.time = time()

	def inConnected_onError( self, event ):
		error = self.socket.getsockopt( SOL_SOCKET, SO_ERROR )
		Dispatcher.notify( NetError( error, None, self.transport, self.localAddress, self.localPort, self.remoteAddress, self.remotePort, connection=self ) )

		self.close( event )

	def inConnected_onUnbind( self, event ):
		self.state = self.STATE_DISCONNECTING

		self.socket.shutdown( SHUT_RDWR )

		self.state = self.STATE_DISCONNECTED

		newEvent = NetEvent( NetEvent.EVENT_DISCONNECTED, self.transport, self.localAddress, self.localPort, self.remoteAddress, self.remotePort, connection=self )
		Dispatcher.notify( newEvent )

	# Unbound

	# Helpers
	def close( self, event ):
		self.state = self.STATE_DISCONNECTING

		self.socket.close()
		self.socket = None

		self.state = self.STATE_DISCONNECTED

		newEvent = NetEvent( NetEvent.EVENT_DISCONNECTED, self.transport, self.localAddress, self.localPort, self.remoteAddress, self.remotePort, connection=self )
		Dispatcher.notify( newEvent )

