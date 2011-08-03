#!/usr/bin/env python
from iron.context import Context
from iron.event import Event
from iron.state import State
from iron.dispatcher import Dispatcher
from mercury.dialog.dialog import *
from mercury.dialog.uas_dialog_invite import *
from mercury.dialog.uas_dialog_subscribe import *
from mercury.message.message import *
from time import sleep
import logging
import unittest

#===============================================================================
class DialogListener(object):
	def query( self, name, active = True, args = None, kwargs = None ):
		if name == 'sip.timer.e':
			return 0.5
		elif name == 'sip.timer.f':
			return 4
		elif name == 'sip.timer.k':
			return 0.25
		else:
			return Node.query( self, name, active, args, kwargs )

#===============================================================================
class TestDialog(unittest.TestCase):
	def runTest( self ):
		d = Dispatcher.getInstance()

		c = Context( 'Root' )
		c.start()

		dialog = UasDialogSubscribe() #FIXME: pass event?
		d.add( obj=dialog, parentObj=None, context=c )

		s = 'SUBSCRIBE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nExpires: 3600\r\nCall-ID: abcd\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = dialog, dstObj = dialog )

		s = 'SIP/2.0 100 Trying\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCall-ID: abcd\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = dialog, dstObj = dialog )

		s = 'SIP/2.0 200 OK\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCall-ID: abcd\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = dialog, dstObj = dialog )

		s = 'SUBSCRIBE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCall-ID: abcd\r\nExpires: 0\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = dialog, dstObj = dialog )

		s = 'SIP/2.0 200 OK\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		e = MessageEvent( MessageEvent.EVENT_RX, message=m, transport='udp', localAddress='127.0.0.1', localPort=9000, remoteAddress='127.0.0.1', remotePort=9001 )
		d.send( e, srcObj = dialog, dstObj = dialog )

		sleep( 4 )

		assert 1

if __name__ == "__main__":
	unittest.main()
