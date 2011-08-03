#!/usr/bin/env python
from iron.context import Context
from iron.dispatcher import Dispatcher
from iron.event import Event
from iron.state import State
from mercury.message.message import *
from mercury.message.message import Message
from mercury.transaction.uac_transaction import UacTransaction
from mercury.transaction.uac_transaction_invite import UacTransactionInvite
from mercury.transaction.uas_transaction import UasTransaction
from mercury.transaction.uas_transaction_invite import UasTransactionInvite
from time import sleep
import logging
import unittest

class TestParent(object):
	def onDefault( self, event, *args, **kwargs ):
		print type(event), str(event), str(args), str(kwargs)

class TestClientTransaction(unittest.TestCase):
	def runTest( self ):
		d = Dispatcher.getInstance()

		c = Context( 'Root' )
		c.start()

		p = TestParent()
		d.add( obj=p, parentObj=None, context=c )

		t = UacTransaction()
		d.add( obj=t, parentObj=p, context=c )
		d.addListener( t, p )

		s = 'SUBSCRIBE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_TX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = p, dstObj = t )
		sleep( 2 )

		s = 'SIP/2.0 100 Trying\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = p, dstObj = t )

		s = 'SIP/2.0 200 OK\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = p, dstObj = t )

		c.stop()

class TestServerTransaction(unittest.TestCase):
	def runTest( self ):
		d = Dispatcher.getInstance()

		c = Context( 'Root' )
		c.start()

		p = TestParent()
		d.add( obj=p, parentObj=None, context=c )

		t = UasTransaction()
		d.add( obj=t, parentObj=None, context=c )
		d.addListener( t, p )

		s = 'SUBSCRIBE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = p, dstObj = t )

		s = 'SIP/2.0 100 Trying\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_TX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = p, dstObj = t )

		s = 'SIP/2.0 200 OK\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_TX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = p, dstObj = t )

		d.send( Event( t.EVENT_TIMER_J ), srcObj = p, dstObj = t )

		c.stop()

class TestClientInviteTransaction(unittest.TestCase):
	def runTest( self ):
		d = Dispatcher.getInstance()

		c = Context( 'Root' )
		c.start()

		p = TestParent()
		d.add( obj=p, parentObj=None, context=c )

		t = UacTransactionInvite()
		d.add( obj=t, parentObj=None, context=c )
		d.addListener( t, p )

		d.send( Event( 'INVITE' ), srcObj = p, dstObj = t )
		d.send( Event( 'TimerA' ), srcObj = p, dstObj = t )
		d.send( Event( '1xx' ), srcObj = p, dstObj = t )
		d.send( Event( '3xx' ), srcObj = p, dstObj = t )
		d.send( Event( 'TimerD' ), srcObj = p, dstObj = t )

		c.stop()

class TestServerInviteTransaction(unittest.TestCase):
	def runTest( self ):
		d = Dispatcher.getInstance()

		c = Context( 'Root' )
		c.start()

		p = TestParent()
		d.add( obj=p, parentObj=None, context=c )

		t = UasTransactionInvite()
		d.add( obj=t, parentObj=None, context=c )
		d.addListener( t, p )

		d.send( Event( 'INVITE' ), srcObj = p, dstObj = t )
		d.send( Event( '1xx'    ), srcObj = p, dstObj = t )
		d.send( Event( '3xx'    ), srcObj = p, dstObj = t )
		d.send( Event( 'TimerG' ), srcObj = p, dstObj = t )
		d.send( Event( 'ACK'    ), srcObj = p, dstObj = t )
		d.send( Event( 'TimerI' ), srcObj = p, dstObj = t )

		c.stop()

if __name__ == "__main__":
	#logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	logging.basicConfig( level=logging.INFO, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

