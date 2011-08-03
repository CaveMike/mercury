#!/usr/bin/env python
from mercury.body.body import Body
from copy import copy
from mercury.core import SipException
from mercury.header.element import *
from mercury.header.elements import *
from mercury.header.header import *
from mercury.header.header import SIP_CRLF
from mercury.message.container import Container
from UserList import UserList
from UserString import MutableString
import unittest
import logging

class TestHeaderBasic(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )
		s = 'Contact: "RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n'
		assert( h.name == 'Contact' )
		#print 'h' + str(h) + 'h'
		#print 's' + str(s) + 's'
		assert( str(h) == s )

class TestHeaderIter(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )

		l = [ str(v) for v in h ]
		s = '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>'
		assert( str(','.join(l)) == s )

class TestHeaderIn(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )
		assert( Address( '"RileyGuy"<sip:riley@cave>' ) in h )

class TestHeaderGetSlice(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )

		s = '"J-Man"<sip:joshua@cave>'
		assert( str(h[2]) == s )

		s = '"MattMan"<sip:matthew@cave>'
		assert( str(h[1]) == s )

		s = '"MattMan"<sip:matthew@cave>'
		assert( str(h[1]) == s )


class TestHeaderGetSliceRange(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )

		l = [ str(v) for v in h[0:2] ]
		s = '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>'
		assert( str(','.join(l)) == s )

class TestHeaderSetSlice(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )
		h[0] = Address( '"RyGuy"<sip:riley@cave>' )
		s = '"RyGuy"<sip:riley@cave>'
		assert( str(h[0]) == s )

class TestHeaderInsert(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )
		h.insert( 3, Address( '"TheBeast"<sip:chloe@cave>' ) )

		l = [ str(v) for v in h ]
		s = '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>,"TheBeast"<sip:chloe@cave>'
		assert( str(','.join(l)) == s )

		h.insert( 4, '"Laura"<sip:laura@cave>' )

		l = [ str(v) for v in h ]
		s = '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>,"TheBeast"<sip:chloe@cave>,"Laura"<sip:laura@cave>'
		assert( str(','.join(l)) == s )

class TestHeaderRepr(unittest.TestCase):
	def runTest( self ):
		h = Header( 'Contact', '"RileyGuy"<sip:riley@cave>,"MattMan"<sip:matthew@cave>,"J-Man"<sip:joshua@cave>\r\n' )
		assert( repr(h) )

class TestContainerBasic(unittest.TestCase):
	def runTest( self ):
		s = 'To: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		c = Container( s )
		#print 's' + str(s) + 's'
		#print 'c' + str(c) + 'c'
		assert( str(c) == s )

class TestContainerMultipart(unittest.TestCase):
	def runTest( self ):
		s = \
'Content-Type: multipart/mixed;boundary=yradnuoB\r\n' \
'Content-Disposition: session\r\n' \
'\r\n' \
'--yradnuoB\r\n' \
'Content-Length: 136\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n' \
'\r\n' \
'--yradnuoB\r\n' \
'Content-Type: message/sipfrag\r\n\r\nBYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n' \
'\r\n' \
'--yradnuoB--\r\n'

		c = Container( s )
		#print 's' + str(s) + 's'
		#print 'c' + str(c) + 'c'
		assert( str(c) == s )

class TestContainerSetStr(unittest.TestCase):
	def runTest( self ):
		c = Container()
		c['Accept'] = 'application/sdp;a=b;x;y;k0=a;z;k1=b'
		c['Allow'] = 'INVITE,BYE,ACK'
		c['Call-ID'] = 'dfasdfasdfasdfasdfas-sdfasdfasdfasdf;0;1'
		c['Contact'] = '"Josh"<sip:joshua@cave>;c'
		c['ContentDisposition'] = 'session;a=b'
		c['ContentLength'] = 1
		c['ContentType'] = 'application/message-info;a=b;x;y;k0=a;z;k1=b'
		c['CSeq'] = '5 PRACK'
		c['Expires'] = '3600;x=y'
		c['From'] = '"RileyMan"<sip:riley@cave>;b'
		c['MaxForwards'] = 70
		c['Server'] = 'servery'
		c['Supported'] = '100rel,timer'
		c['To'] = '"Matt"<sip:matthew@cave>;a'
		c['Unsupported'] = 'newage,crackers'
		c['UserAgent'] = 'useragency'
		c['Via'] = 'SIP/2.0/UDP sip.cave.com;q;r;s'

		s = \
'Accept: application/sdp;x;y;z;a=b;k1=b;k0=a\r\n' \
'Allow: INVITE,BYE,ACK\r\n' \
'Call-ID: dfasdfasdfasdfasdfas-sdfasdfasdfasdf;0;1\r\n' \
'Contact: "Josh"<sip:joshua@cave>;c\r\n' \
'ContentDisposition: session;a=b\r\n' \
'ContentLength: 1\r\n' \
'ContentType: application/message-info;x;y;z;a=b;k1=b;k0=a\r\n' \
'CSeq: 5 PRACK\r\n' \
'Expires: 3600;x=y\r\n' \
'From: "RileyMan"<sip:riley@cave>;b\r\n' \
'MaxForwards: 70\r\n' \
'Server: servery\r\n' \
'Supported: 100rel,timer\r\n' \
'To: "Matt"<sip:matthew@cave>;a\r\n' \
'Unsupported: newage,crackers\r\n' \
'UserAgent: useragency\r\n' \
'Via: SIP/2.0/UDP sip.cave.com;q;r;s\r\n' \
'\r\n'
		#print 's' + str(s) + 's'
		#print 'c' + str(c) + 'c'
		assert( str(c) == s )

class TestContainerDuplicate(unittest.TestCase):
	def runTest( self ):
		c = Container()

		c['ContentLength'] = 0
		c['ContentLength'] = 1

		s = \
'ContentLength: 1\r\n' \
'\r\n'
		#print 's' + str(s) + 's'
		#print 'c' + str(c) + 'c'
		assert( str(c) == s )

class TestContainerMissing(unittest.TestCase):
	def runTest( self ):
		c = Container()
		assert( c['missing'] == None )

class TestContainerRepr(unittest.TestCase):
	def runTest( self ):
		s = \
'Content-Type: multipart/mixed; boundary=yradnuoB\r\n' \
'Content-Disposition: session\r\n' \
'\r\n' \
'--yradnuoB\r\n' \
'Content-Length: 134\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n' \
'--yradnuoB\r\n' \
'Content-Type: message/sipfrag\r\n\r\nBYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n' \
'--yradnuoB--\r\n' \
'\r\n'
		c = Container( s )
		assert( repr(c) )

if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

