#!/usr/bin/env python
from mercury.uri.uri import Uri
from mercury.core import SipException
from mercury.uri.sip_uri import SipUri
import logging
import unittest

class TestUriAll(unittest.TestCase):
	def runTest( self ):
		x = SipUri()

		self.assertRaises( SipException, self.TestUri, 'sip:' )

		self.TestUri( 'tel:5551212;phone-context=home' )
		self.TestUri( 'sip:host' )
		self.TestUri( 'sip:host:8000' )
		self.TestUri( 'sip:user@host' )
		self.TestUri( ' sip:user@host', 'sip:user@host' )
		self.TestUri( 'sip:user@host ', 'sip:user@host' )
		self.TestUri( ' sip:user@host ', 'sip:user@host' )
		self.TestUri( 'sip:user:password@host' )
		self.TestUri( 'sip:user:password@host:5060' )
		self.TestUri( 'sip:user:pass@host:5060;p0;kp0=a;p1;kp1=b;p2;kp2=c', 'sip:user:pass@host:5060;p0;p1;p2;kp0=a;kp1=b;kp2=c' )
		self.TestUri( 'sip:user:pass@host:5060?h0&h1&h2' )
		self.TestUri( 'sip:user:pass@host:5060?hp0=a&hp1=b&hp2=c', 'sip:user:pass@host:5060?hp2=c&hp1=b&hp0=a' )
		self.TestUri( 'sip:user:pass@host:5060?h0&hp0=a&h1&hp1=b&h2&hp2=c', 'sip:user:pass@host:5060?h0&h1&h2&hp2=c&hp1=b&hp0=a' )
		self.TestUri( 'sip:user:pass@host:5060;p0;kp0=a;p1;kp1=b;p2;kp2=c?h0&hp0=a&h1&hp1=b&h2&hp2=c', 'sip:user:pass@host:5060;p0;p1;p2;kp0=a;kp1=b;kp2=c?h0&h1&h2&hp2=c&hp1=b&hp0=a' )
		self.TestUri( 'sips:user:pass@host:5060;p0;kp0=a;p1;kp1=b;p2;kp2=c?h0&hp0=a&h1&hp1=b&h2&hp2=c', 'sips:user:pass@host:5060;p0;p1;p2;kp0=a;kp1=b;kp2=c?h0&h1&h2&hp2=c&hp1=b&hp0=a' )

		uri = Uri( 'sip:host:8000' )
		uri.hostPort = 'cave:5060'
		assert( uri.hostPort == 'cave:5060' )
		assert( uri.host == 'cave' )
		assert( uri.port == 5060 )
		uri.userPassword = 'josh:icecream'
		assert( uri.userPassword == 'josh:icecream' )
		assert( uri.user == 'josh' )
		assert( uri.password == 'icecream' )

	def TestUri( self, i, o = None ):
		if not o:
			o = i
		#print i
		uri = Uri( i )
		#print str(uri)
		#print uri.dump()
		assert( o == str(uri) )

#-------------------------------------------------------------------------------
if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

