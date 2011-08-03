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
from time import time
import logging
import unittest
from iron.context import Context
from mercury.network.test_helpers import TestListener
from mercury.network.test_helpers import TestConfiguration
from time import sleep
from mercury.network.udp_binding import UdpBinding

class TestUdp(unittest.TestCase):
	def runTest( self ):
		c = Context( 'Root' )
		c.start()

		l = TestListener()
		Dispatcher.add( l, context = c )

		config = TestConfiguration()

		e = NetEvent( NetEvent.EVENT_BIND, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ) )

		o = UdpBinding( e )
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

		e = NetEvent( BindingBase.EVENT_QUEUE, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ), remoteAddress=config.query( 'network.remoteAddress' ), remotePort=config.query( 'network.remotePort' ), packet=packet )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		e = NetEvent( BindingBase.EVENT_WRITE, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ), remoteAddress=config.query( 'network.remoteAddress' ), remotePort=config.query( 'network.remotePort' ) )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		e = NetEvent( BindingBase.EVENT_READ, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ), remoteAddress=config.query( 'network.remoteAddress' ), remotePort=config.query( 'network.remotePort' ) )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		e = NetEvent( NetEvent.EVENT_UNBIND, transport='udp', localAddress=config.query( 'network.localAddress' ), localPort=config.query( 'network.localPort' ) )
		Dispatcher.send( e, srcObj=l, dstObj=o )
		sleep( config.query( 'test.timeout' ) )

		c.stop()

if __name__ == "__main__":
	import logging

	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

