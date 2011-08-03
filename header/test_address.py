#!/usr/bin/env python
from mercury.header.elements import Address
import logging
import unittest

class TestAddressAll(unittest.TestCase):
	def runTest( self ):
		self.TestAddress( 'sip:host', '<sip:host>' )
		self.TestAddress( '"name"sip:host', '"name"<sip:host>' )
		self.TestAddress( '"name"sip:host;a;b;c', '"name"<sip:host>;a;b;c' )
		self.TestAddress( '"name"<sip:host>', '"name"<sip:host>' )
		self.TestAddress( '"name"<sip:host>;x0;x1;x2', '"name"<sip:host>;x0;x1;x2' )
		self.TestAddress( '"name"<sip:host>;y0=a;y1=b;y2=c', '"name"<sip:host>;y1=b;y0=a;y2=c' )
		self.TestAddress( '"name"<sip:host>;x0;y0=a;x1;y1=b;x2;y2=c', '"name"<sip:host>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( '"name"<sip:user:password@host:5060>;x0;y0=a;x1;y1=b;x2;y2=c', '"name"<sip:user:password@host:5060>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( '"name"<sip:user:pass@host:5060;p0;kp0=a;p1;kp1=b;p2;kp2=c?h0&hp0=a&h1&hp1=b&h2&hp2=c>;x0;y0=a;x1;y1=b;x2;y2=c', '"name"<sip:user:pass@host:5060;p0;p1;p2;kp0=a;kp1=b;kp2=c?h0&h1&h2&hp2=c&hp1=b&hp0=a>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( '"name"<sip:host>;x0;y0=a;x1;y1=b;x2;y2=c,z0;z1;z2;w0=x;w1=y;w2=z', '"name"<sip:host>;x0;x1;x2;z0;z1;z2;w2=z;w1=y;w0=x;y1=b;y0=a;y2=c' )

		self.TestAddress( '<sip:host>', '<sip:host>' )
		self.TestAddress( '<sip:host>;x0;x1;x2', '<sip:host>;x0;x1;x2' )
		self.TestAddress( '<sip:host>;y0=a;y1=b;y2=c', '<sip:host>;y1=b;y0=a;y2=c' )
		self.TestAddress( '<sip:host>;x0;y0=a;x1;y1=b;x2;y2=c', '<sip:host>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( '<sip:user:password@host:5060>;x0;y0=a;x1;y1=b;x2;y2=c', '<sip:user:password@host:5060>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( '<sip:user:pass@host:5060;p0;kp0=a;p1;kp1=b;p2;kp2=c?h0&hp0=a&h1&hp1=b&h2&hp2=c>;x0;y0=a;x1;y1=b;x2;y2=c', '<sip:user:pass@host:5060;p0;p1;p2;kp0=a;kp1=b;kp2=c?h0&h1&h2&hp2=c&hp1=b&hp0=a>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( '<sip:host>;x0;y0=a;x1;y1=b;x2;y2=c,z0;z1;z2;w0=x;w1=y;w2=z', '<sip:host>;x0;x1;x2;z0;z1;z2;w2=z;w1=y;w0=x;y1=b;y0=a;y2=c' )

		self.TestAddress( 'sip:host', '<sip:host>' )
		self.TestAddress( 'sip:host;a;b;c', '<sip:host>;a;b;c' )
		self.TestAddress( 'sip:host', '<sip:host>' )
		self.TestAddress( 'sip:host;x0;x1;x2', '<sip:host>;x0;x1;x2' )
		self.TestAddress( 'sip:host;y0=a;y1=b;y2=c', '<sip:host>;y1=b;y0=a;y2=c' )
		self.TestAddress( 'sip:host;x0;y0=a;x1;y1=b;x2;y2=c', '<sip:host>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( 'sip:user:password@host:5060;x0;y0=a;x1;y1=b;x2;y2=c', '<sip:user:password@host:5060>;x0;x1;x2;y1=b;y0=a;y2=c' )
		self.TestAddress( 'sip:user:pass@host:5060;p0;kp0=a;p1;kp1=b;p2;kp2=c?h0&hp0=a&h1&hp1=b&h2&hp2=c;x0;y0=a;x1;y1=b;x2;y2=c', '<sip:user:pass@host:5060>;p0;p1;p2;x0;x1;x2;kp0=a;kp1=b;kp2=c?h0&hp0=a&h1&hp1=b&h2&hp2=c;y1=b;y0=a;y2=c' )
		self.TestAddress( 'sip:host;x0;y0=a;x1;y1=b;x2;y2=c,z0;z1;z2;w0=x;w1=y;w2=z', '<sip:host>;x0;x1;x2;z0;z1;z2;w2=z;w1=y;w0=x;y1=b;y0=a;y2=c' )

	def TestAddress( self, i, o = None ):
		if not o:
			o = i

		#print i
		address = Address( i )
		#print str(address)
		#print address.dump()
		assert( o == str(address) )

if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

