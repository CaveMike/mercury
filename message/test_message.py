#!/usr/bin/env python
from copy import copy
from iron.event import Event
from mercury.core import SipException
from mercury.header.element import *
from mercury.header.elements import *
from mercury.header.header import *
from mercury.header.header import SIP_CRLF
from mercury.message.container import *
from mercury.uri.uri import *
from sys import modules
from time import time
from UserString import MutableString
from mercury.message.message import *
from sys import modules
from mercury.uri.sip_uri import SipUri
from mercury.uri.sips_uri import SipsUri
from mercury.message.message_assembler import *
import unittest
import logging

#===============================================================================
class TestGet(unittest.TestCase):
	def runTest( self ):

		m = Request()

		try:
			m['To'] = None
		except SipException:
			pass

		assert( not m['To'] )
		m['To'] = ''
		assert( m['To'] )

		m['To'].name = 'RileyMan'
		m['To'].uri = 'sip:riley@cave;x'
		m['To'].params.append( 'y' )
		#print m['To'].name
		#print str(m['To'])
		assert( str(m['To']) == '"RileyMan"<sip:riley@cave;x>;y' )

		try:
			m['To'] = None
		except SipException:
			pass

#===============================================================================
class TestSet(unittest.TestCase):
	def runTest( self ):

		x = '"Josh"<sip:joshua@cave>'

		m = Request()

		m['To'] = x
		#print str(m['To'])
		assert( str(m['To']) == (x) )

#===============================================================================
class TestDelete(unittest.TestCase):
	def runTest( self ):

		m = Request()

		del m['To']
		assert( not m.__dict__.has_key('To') )

#===============================================================================
class TestParse(unittest.TestCase):
	def runTest( self ):

		m = Request()

		m['To'] = '"MattMan"<sip:matthew@cave>'
		assert( str(m['To']) == '"MattMan"<sip:matthew@cave>' )

		m['To'] = '"Matt"sip:matthew@cave'
		assert( str(m['To']) == '"Matt"<sip:matthew@cave>' )

		m['To'].name = 'Matty'
		m['To'].params.append( 'xyz' )
		#print str(m['To'])
		assert( str(m['To']) == '"Matty"<sip:matthew@cave>;xyz' )

#===============================================================================
class TestPrint(unittest.TestCase):
	def runTest( self ):

#		m = Message( method = 'BYE', requestUri = 'sip:chloe@cave;treats' )
		m = Request()

		m.method = 'BYE'
		m.requestUri = 'sip:chloe@cave;treats'

		m['To'] = '"Matt"<sip:matthew@cave>'
		m['From'] = '"Josh"<sip:joshua@cave>'
		m['Contact'] = '"RileyMan"<sip:riley@cave>'

		s = 'BYE sip:chloe@cave;treats SIP/2.0\r\n' \
'To: "Matt"<sip:matthew@cave>\r\n' \
'From: "Josh"<sip:joshua@cave>\r\n' \
'Contact: "RileyMan"<sip:riley@cave>\r\n' \
'\r\n'
		#print str(m)
		#print str(s)
		assert( str(m) == s )

#===============================================================================
class TestMessageAll(unittest.TestCase):
	def runTest( self ):

		s = 'BYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Message( s )
		#print m.dump()
		assert( isinstance( m, Request ) )

		m.method = 'BYE'
		#print m.dump()
		assert( m.method == 'BYE' )

		s = 'SIP/2.0 403 User Not Found\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nCSeq: 5 PRACK\r\n\r\n'
		m = Message( s )
		assert( isinstance( m, Response ) )

		s = 'SIP/2.0 403 User Not Found\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\n\r\n'
		m = Response( s )
		#print m.dump()
		assert( isinstance( m, Response ) )

#===============================================================================
class TestUserAgent(unittest.TestCase):
	def runTest( self ):

		s = 'BYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n\r\n'
		m = Message( s )
		#print m.dump()
		assert( isinstance( m, Request ) )

#===============================================================================
class TestHeaders(unittest.TestCase):
	def runTest( self ):

		h = Request()
		h.method = 'BYE'
		h.requestUri = 'sip:chloe@cave;treats'

		h['Accept'] = 'application/sdp;a=b;x;y;k0=a;z;k1=b'
		h['Allow'] = 'INVITE,BYE,ACK'
		h['Call-ID'] = '43453454-4353423453;q;r;s'
		h['Contact'] = '"Josh"<sip:joshua@cave>;c'
		h['ContentDisposition'] = 'session;a=b'
		h['ContentLength'] = 0
		h['ContentType'] = 'application/message-info;a=b;x;y;k0=a;z;k1=b'
		h['CSeq'] = '5 PRACK'
		h['CSeq'].value = 12
		h['Expires'] = '3600;x=y'
		h['From'] = '"RileyMan"<sip:riley@cave>;b'
		h['MaxForwards'] = 70
		h['Server'] = 'servery'
		h['Supported'] = '100rel,timer'
		h['To'] = '"Matt"<sip:matthew@cave>;a'
		h['Unsupported'] = 'newage,crackers'
		h['UserAgent'] = 'useragency'
		h['Via'] = 'SIP/2.0/UDP sip.cave.com;q;r;s'
		h['Unknown'] = 'unknown;1=a;b;c;4=d'

		#print '1a: "' + str(h['To']) + '"'
		#print '1b: "' + str(h['From']) + '"'
		#print '1c: "' + str(h['Contact']) + '"'
		#print '1d: "' + str(h.useragent) + '"'
		#print '2: "' + str(h) + '"'
		#print '3: "' + h.dump() + '"'
		#print '4a: "' + h['To'].dump() + '"'
		#print '4b: "' + h['From'].dump() + '"'
		#print '4c: "' + h['Contact'].dump() + '"'
		#print '4d: "' + h.useragent.dump() + '"'
#		del h.useragent

#		h['To'] = str(h['Contact'])

		#print '5: \n' + str(h)
		#print '6: ' + str(h.headers)
		#print '7: ' + h['To'].raw

#		del h.headers

		assert( 1 )

#===============================================================================
class TestNewHeaders(unittest.TestCase):
	def runTest( self ):

		h = Request()
		h.method = 'BYE'
		h.requestUri = 'sip:chloe@cave;treats'

		h['Accept'] = 'application/sdp;a=b;x;y;k0=a;z;k1=b'
		h['Allow'] = 'INVITE,BYE,ACK'
		h['Call-ID'] = 'dfasdfasdfasdfasdfas-sdfasdfasdfasdf;0;1'
		h['Contact'] = '"Josh"<sip:joshua@cave>;c'
		h['ContentDisposition'] = 'session;a=b'
		h['ContentLength'] = 0
		h['ContentLength'] = 1
		h['ContentType'] = 'application/message-info;a=b;x;y;k0=a;z;k1=b'
		h['CSeq'] = '5 PRACK'
		h['Expires'] = '3600;x=y'
		h['From'] = '"RileyMan"<sip:riley@cave>;b'
		h['MaxForwards'] = 70
		h['Server'] = 'servery'
		h['Supported'] = '100rel,timer'
		h['To'] = '"Matt"<sip:matthew@cave>;a'
		h['Unsupported'] = 'newage,crackers'
		h['UserAgent'] = 'useragency'
		h['Via'] = 'SIP/2.0/UDP sip.cave.com;q;r;s'


		#print '1a: "' + str(h['To']) + '"'
		#print '1b: "' + str(h['From']) + '"'
		#print '1c: "' + str(h['Contact']) + '"'
		#print '1d: "' + str(h.useragent) + '"'
		#print '2: "' + str(h) + '"'
		#print '3: "' + h.dump() + '"'
		#print '4a: "' + h['To'].dump() + '"'
		#print '4b: "' + h['From'].dump() + '"'
		#print '4c: "' + h['Contact'].dump() + '"'
		#print '4d: "' + h['User-Agent'].dump() + '"'
#		del h.useragent

#		h['To'] = str(h['Contact'])

		#print '5: \n' + str(h)
		#print '6: ' + str(h.headers)
		#print '7: ' + h['To'].raw

#		del h.headers

		assert( 1 )

#===============================================================================
class TestSMS(unittest.TestCase):
	def runTest( self ):

		s = 'INVITE sip:bob@biloxi.example.com SIP/2.0\r\nContent-Length: 134\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n'
		m = Request( s )
 		#print str(m)
 		#print str(m.body)

#===============================================================================
class TestMultipart(unittest.TestCase):
	def runTest( self ):

		s = 'INVITE sip:bob@biloxi.example.com SIP/2.0\r\n' \
'Content-Type: multipart/mixed; boundary=yradnuoB\r\n' \
'Content-Disposition: session\r\n' \
'\r\n' \
'--yradnuoB\r\n' \
'Content-Length: 134\r\nContent-Type: application/simple-message-summary\r\n\r\nMessages-Waiting: yes\r\nMessage-Account: sip:mailbox@biloxi.example.com\r\nvoice-message: 1/5(2/4)\r\nfax-message: 0/1\r\ntext-message: 3/7\r\n' \
'--yradnuoB\r\n' \
'Content-Type: message/sipfrag\r\n\r\nBYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n' \
'--yradnuoB--\r\n' \
'\r\n'
		m = Request( s )

		# Get a specific body based on Content-Type.
		l = [ body for body in m.body.bodies if body['Content-Type'].type == 'application' ]
		#print l
		for body in l:
			pass
			#print type(body)
			#print body

		# Get a specific body based on Content-Type.
		l = [ body for body in m.body.bodies if body['Content-Type'].type == 'message' ]
		#print l
		for body in l:
			pass
			#print type(body)
			#print body

		# Iterate through each body.
		for body in m.body.bodies:
			pass
			#print type(body)
			#print type(body.body)

		# Iterate through each body using the built-in iterator.
		#print '\n\nIterating through all'
		for body in m.iterBodies():
			pass
			#print type(body)
#			print body

#===============================================================================
class TestSipfrag(unittest.TestCase):
	def runTest( self ):

		s = 'INVITE sip:bob@biloxi.example.com SIP/2.0\r\n' \
'Content-Type: message/sipfrag\r\n' \
'\r\n' \
'BYE sip:chloe@cave;treats SIP/2.0\r\nTo: "Matt"<sip:matthew@cave>\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\n\r\n'

		m = Request( s )
		#print m
		#print m.body

		# Iterate through each body using the built-in iterator.
		#print '\n\nIterating through all'
		for body in m.iterBodies():
			pass
			#print type(body)
#			print body

#===============================================================================
class TestAllow(unittest.TestCase):
	def runTest( self ):

		s = 'INVITE sip:bob@biloxi.example.com SIP/2.0\r\n' \
'Allow: INVITE,BYE,ACK\r\n' \
'\r\n'
		m = Request( s )
		#print 'Allow"' + str(m['Allow']) + '"'
		#for element in m['Allow']:
		#	print '"' + str(element) + '"'

		#print 'raw', m['Allow'].raw

#===============================================================================
class TestResponse(unittest.TestCase):
	def runTest( self ):
		s = 'BYE sip:chloe@cave;treats SIP/2.0\r\nVia: SIP/2.0/UDP sip.cave.com;q;r;s\r\nCSeq: 78 BYE\r\nTo: "Matt"<sip:matthew@cave>;w;x;y;z\r\nContact: "RileyMan"<sip:riley@cave>\r\nFrom: "Josh"<sip:joshua@cave>\r\nUser-Agent: useragent\r\nCall-ID: xyz-123\r\n\r\n'
		request = Request( s )
		assert( isinstance( request, Request ) )

		response = createResponse( request, 200 )
		#print response
		assert( isinstance( response, Response ) )

		assert( request['To'] == response['To'] )
		assert( str(request['To']) == str(response['To']) )
		assert( request['From'] == response['From'] )
		assert( str(request['From']) == str(response['From']) )
		assert( request['Call-ID'] == response['Call-ID'] )
		assert( str(request['Call-ID']) == str(response['Call-ID']) )
		assert( request['CSeq'] == response['CSeq'] )
		assert( str(request['CSeq']) == str(response['CSeq']) )
		assert( request['Via'] == response['Via'] )
		assert( str(request['Via']) == str(response['Via']) )

		copiedHeaders = [ 'To', 'From', 'Call-ID', 'CSeq', 'Via' ]
		for headerName in copiedHeaders:
			assert( request[headerName] == response[headerName] )
			assert( str(request[headerName]) == str(response[headerName]) )

#===============================================================================
#class TestParams(unittest.TestCase):
#	def runTest( self ):
#		p0 = Params( ';a;b;c;d=0;e=1;f=2' )
#		p1 = Params( ';a;b;c;d=0;e=1;f=2' )
#		assert( p0 == p1 )
#
#		p0 = Params( ';a;b;c;d=0;e=1;f=2' )
#		p1 = Params( ';d=0;f=2;b;e=1;a;c' )
#		assert( p0 == p1 )
#
#		h0 = HParams( '?a&b&c&d=0&e=1&f=2' )
#		h1 = HParams( '?a&b&c&d=0&e=1&f=2' )
#		assert( h0 == h1 )
#
#		h0 = HParams( '?a&b&c&d=0&e=1&f=2' )
#		h1 = HParams( '?d=0&a&c&e=1&b&f=2' )
#		assert( h0 == h1 )

#===============================================================================
#class TestMIMEVersionHeader(unittest.TestCase):
#	def runTest( self ):
#		e = MIMEVersionHeader( '1.2' )
#		print str(e)


#-------------------------------------------------------------------------------
if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

