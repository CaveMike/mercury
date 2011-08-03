#!/usr/bin/env python
from mercury.core import SipException
from mercury.header.header import SIP_CRLF
from mercury.message.message import Message
import unittest
import logging
from mercury.message.message_assembler import *

class TestReassembly(unittest.TestCase):
	def runTest( self ):
		self.tcp()
		self.udp()

	def tcp( self ):
		reassembler = StreamReassembler()

		s = \
'\r\n'
		print 'm0.1', str( reassembler.parse( s ) )

		s = \
'INVITE sip:bob@biloxi.example.com SIP/2.0\r\n' \
'Content-Type: multipart/mixed; boundary=yradnuoB\r\n'
		print 'm0.4', str( reassembler.parse( s ) )

		s = \
'Content-Disposition: session\r\n' \
'Content-Length: 438\r\n' \
'\r\n'
		print 'm0.5', str( reassembler.parse( s ) )

		s = \
'\r\n' \
'--yradnuoB\r\n' \
'Content-Length: 134\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n' \
'--yradnuoB\r\n'
		print 'm1', str( reassembler.parse( s ) )

		s = \
'Content-Type: message/sipfrag\r\n\r\nBYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n' \
'--yradnuoB--\r\n' \
'\r\n'
		print 'm2', str( reassembler.parse( s ) )

	def udp( self ):
		reassembler = DatagramReassembler()

		s = \
'\r\n'
		print 'm0.1', str( reassembler.parse( s ) )

		s = \
'INVITE sip:bob@biloxi.example.com SIP/2.0\r\n' \
'Content-Type: multipart/mixed; boundary=yradnuoB\r\n'
		print 'm0.4', str( reassembler.parse( s ) )

		s = \
'Content-Disposition: session\r\n' \
'Content-Length: 438\r\n' \
'\r\n'
		print 'm0.5', str( reassembler.parse( s ) )

		s = \
'\r\n' \
'--yradnuoB\r\n' \
'Content-Length: 134\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n' \
'--yradnuoB\r\n'
		print 'm1', str( reassembler.parse( s ) )

		s = \
'Content-Type: message/sipfrag\r\n\r\nBYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n' \
'--yradnuoB--\r\n' \
'\r\n'
		print 'm2', str( reassembler.parse( s ) )

if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

