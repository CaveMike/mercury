from time import sleep
from context import Context
from event import Event
from lognode import LogNode
from node import Node
from statenode import StateNode
from log4py import Logger
from system import System
from message import *
import unittest

#===============================================================================
class TestListener(LogNode):

	def query( self, name, active = True, args = None, kwargs = None ):
		if name == '':
			return
		else:
			return Node.query( self, name, active, args, kwargs )

#===============================================================================
class Commands(unittest.TestCase):
	def runTest( self ):

		context = Context( 'context' )
		context.start()

		listener = TestListener()
		listener.context = context

		node = System( 'system0', listener )
		node.addListener( listener )

		assert( node.currentState == 'Stopped' )

		node.process( Event( 'Start' ) )
		assert( node.currentState == 'Started' )

		sleep( 2 )

		node.process( Event( 'Pause' ) )
		assert( node.currentState == 'Paused' )

		node.process( Event( 'Continue' ) )
		assert( node.currentState == 'Started' )

		node.process( Event( 'Stop' ) )
		assert( node.currentState == 'Stopped' )

#===============================================================================
class Net(unittest.TestCase):
	def runTest( self ):

		context = Context( 'context' )
		context.start()

		listener = TestListener()
		listener.context = context

		node = System( 'system0', listener )
		node.addListener( listener )

		node.process( Event( 'Start' ) )

		s = 'SUBSCRIBE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nCall-ID: 12345\r\nCSeq: 16 SUBSCRIBE\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress=node.query( 'network.localAddress' ), localPort=node.query( 'network.localPort' ), remoteAddress=node.query( 'network.remoteAddress' ), remotePort=node.query( 'network.remotePort' ) )
		context.queue( e, node )
		sleep( 2 )

#===============================================================================
class xxx(unittest.TestCase):
	def runTest( self ):
		context = Context( 'root' )
		context.start()

		listener = TestListener()
		listener.context = context

		node = System( 'system', listener )
		node.addListener( listener )

		context.queue( Event( System.EVENT_START ), node )

#		from message import *
		s = 'INVITE sip:1@sip.example.com SIP/2.0\r\n' \
'Call-ID: abcde\r\nContent-Length: 136\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n' \
'\r\n'
		message = Request( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message )
		context.queue( e, node )

		#context.queue( Event( System.EVENT_STOP ), node )
		context.stop()

if __name__ == "__main__":
	import logging
	from logging import StreamHandler
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	#logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	#logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()
