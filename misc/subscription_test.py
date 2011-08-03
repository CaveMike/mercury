from dialog import *
from context import Context
from event import Event
from lognode import LogNode
from node import Node
from statenode import *
from log4py import Logger
from message import *
from time import sleep
from uac_subscription import *
import unittest

#===============================================================================
class UacSubscriptionListener(LogNode):

	def query( self, name, active = True, args = None, kwargs = None ):
		if name == 'sip.timer.e':
			return 4
		elif name == 'sip.timer.f':
			return 4
		elif name == 'sip.timer.k':
			return 4
		else:
			return Node.query( self, name, active, args, kwargs )

#===============================================================================
class TestUacSubscription(unittest.TestCase):
	def runTest( self ):

		context = Context( 'context' )
		context.start()

		listener = UacSubscriptionListener()
		listener.context = context

		subscription = UacSubscription( 'subscription0', listener, subscriptionSource='', user='chloe', resourceUri=Uri('bones', 'cave'), event='whats-to-eat', contentType=ContentType('food', 'xml'), expires=3600 )

		context.queue( Event( subscription.EVENT_SUBSCRIBE ), subscription )

		s = 'SIP/2.0 100 Trying\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCall-ID: abcd\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		context.queue( e, subscription )

		s = 'SIP/2.0 200 OK\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCall-ID: abcd\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		context.queue( e, subscription )

		context.queue( Event( subscription.EVENT_UNSUBSCRIBE ), subscription )

		s = 'SIP/2.0 200 OK\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCall-ID: abcd\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		context.queue( e, subscription )

		sleep( 0.5 )

		assert 1

if __name__ == "__main__":
	unittest.main()
