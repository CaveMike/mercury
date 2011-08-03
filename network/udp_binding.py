#! /usr/bin/python
from iron.delegator import Delegator
from iron.dispatcher import Dispatcher
from mercury.network.netevent import NetError
from mercury.network.netevent import NetEvent
from mercury.network.network import BindingBase
from Queue import Queue
from select import select
from socket import AF_INET
from socket import error
from socket import SO_ERROR
from socket import SO_REUSEADDR
from socket import SOCK_DGRAM
from socket import socket
from socket import SOL_SOCKET
from iron.state import StateEvent
from iron.state import State
from time import time
import logging

#===============================================================================
class UdpBinding(BindingBase):
	DEFAULT_CONFIGURATION = \
	{ \
		'network.maxmessage'    : 2048, \

		'network.recvfromflags' : 0,    \
		'network.sendtoflags'   : 0,    \
	}

	def __init__( self, event ):
		super( UdpBinding, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )

		self.transport    = event.transport
		self.localAddress = event.localAddress
		self.localPort    = event.localPort

		self.socket = None
		self.__queue = Queue()

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

	def readyToRead( self ):
		return self.socket and self.state == self.STATE_BOUND

	def readyToWrite( self ):
		return self.socket and self.state == self.STATE_BOUND and not self.__queue.empty()

	def readyToError( self ):
		return self.socket and self.state == self.STATE_BOUND

	def __str__( self ):
		return '%s(%s:%s)' % ( str(self.transport), str(self.localAddress), str(self.localPort) )

	# Initial
	def inInitial_onBind( self, event ):
		self.state = self.STATE_BINDING

		self.socket = socket( AF_INET, SOCK_DGRAM )
		self.socket.setblocking( 0 )
		self.socket.bind( ( self.localAddress, self.localPort ) )
		self.socket.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )

		event.binding = self
		self.state = self.STATE_BOUND
		Dispatcher.notify( StateEvent( State.EVENT_STATE_CHANGE, self.state, self.STATE_INITIAL ) )

	# Bound
	def inBound_onQueue( self, event ):
		if ( event.localAddress != self.localAddress ) or ( event.localPort != self.localPort ):
			# This is not our binding.
			return False

		self.__queue.put( event )
		return True

	def inBound_onRead( self, event ):
		if self.socket:
			try:
				buffer, source = self.socket.recvfrom( self.query( 'network.maxmessage' ), self.query( 'network.recvfromflags' ) )
				self.log.info( 'recvfrom:\n%s(%s:%s %s:%s)\n%s.' % ( str(self.transport), str(self.localAddress), str(self.localPort), str(source[0]), str(source[1]), str(buffer) ) )

				newEvent = NetEvent( NetEvent.EVENT_RX_PACKET, self.transport, self.localAddress, self.localPort, remoteAddress=source[0], remotePort=source[1], packet=str(buffer) )
				Dispatcher.notify( newEvent )
			except error, e:
				newEvent = NetError( e[0], e[1], self.transport, self.localAddress, self.localPort )
				Dispatcher.notify( newEvent )

	def inBound_onWrite( self, event ):
		if not self.__queue.empty():
			newEvent = self.__queue.get()

			bytes = self.socket.sendto( newEvent.packet, self.query( 'network.sendtoflags' ), (newEvent.remoteAddress, newEvent.remotePort) )
			self.log.info( 'sendto:\n%s(%s:%s %s:%s)\n%s.' % ( str(self.transport), str(self.localAddress), self.localPort, str(newEvent.remoteAddress), str(newEvent.remotePort), str(newEvent.packet) ) )

			event.time = time()

	def inBound_onError( self, event ):
		error = self.socket.getsockopt( SOL_SOCKET, SO_ERROR )
		Dispatcher.notify( NetError( error, None, self.transport, self.localAddress, self.localPort ) )

	def inBound_onUnbind( self, event ):
		self.state = self.STATE_UNBINDING

		self.socket.close()
		self.socket = None

		event.binding = self
		self.state = self.STATE_UNBOUND
		Dispatcher.notify( StateEvent( State.EVENT_STATE_CHANGE, self.state, self.STATE_BOUND ) )

	# Unbound

