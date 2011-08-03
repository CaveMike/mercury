#!/usr/bin/env python
from carbon.importer import importExtension
from carbon.helpers import nestedproperty
from mercury.core import SipException
from mercury.header.element import HParams
from mercury.header.element import IElement
from mercury.header.element import Params
from UserString import MutableString
import logging
import unittest

class SipUri(IElement):
	def __init__( self, value = None ):
		super( SipUri, self ).__init__( value )
		self.protocol = None
		self.user = None
		self.password = None
		self.host = None
		self.port = None
		self.params = []
		self.kparams = {}
		self.hparams = []
		self.hkparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
		if self.protocol != other.protocol:
			return self.protocol.__cmp__( other.protocol )

		if self.user != other.user:
			return self.user.__cmp__( other.user )

		if self.password != other.password:
			return self.password.__cmp__( other.password )

		if self.host != other.host:
			return self.host.__cmp__( other.host )

		if self.port != other.port:
			return self.port.__cmp__( other.port )

		n = Params.__cmp__( self.params, self.kparams, other.params, other.kparams )
		if n != 0:
			return n

		n = HParams.__cmp__( self.hparams, self.hkparams, other.hparams, other.hkparams )
		if n != 0:
			return n

		return 0

	def parse( self, value ):
		try:
			n = value.find( ':' )
			if n < 0:
				raise SipException( 'Failed to parse protocol of URI, ' + value + '.' )
			self.protocol = value[:n]
			value = value[n+1:]

			n = value.find( '@' )
			if n < 0:
				self.host = value
			else:
				self.host = value[n+1:]
				self.user = value[:n]

			if self.user:
				n = self.user.find( ':' )
				if n >= 0:
					self.password = self.user[n+1:]
					self.user = self.user[:n]

			self.host = HParams.parse( self.hparams, self.hkparams, self.host )

			self.host = Params.parse( self.params, self.kparams, self.host )

			n = self.host.find( ':' )
			if n >= 0:
				self.port = int( self.host[n+1:] )
				self.host = self.host[:n]

			if not self.host:
				raise SipException( 'Failed to parse host of URI, ' + value + '.' )
		except not SipException:
			raise SipException( 'Failed to parse the URI, ' + value + '.' )


	def build( self ):
		s = MutableString()

		if self.protocol:
			s += self.protocol
			s += ':'

		if self.user:
			s += self.user
			if self.password:
				s += ':'
				s += self.password
			s += '@'

		if not self.host:
			raise SipException( 'Host not specified' )

		s += self.host

		if self.port:
			s += ':'
			s += str(self.port)

		s += Params.build( self.params, self.kparams )

		s += HParams.build( self.hparams, self.hkparams )

		return str(s)

	def validate( self, thorough = False ):
		if not self.protocol:
			raise SipException( 'Invalid protocol in URI, ' + str(self) + '.' )

		if not self.host:
			raise SipException( 'Invalid host in URI, ' + str(self) + '.' )

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'protocol:\'' + str(self.protocol) + '\'' + ', '
		s += 'user:\'' + str(self.user) + '\'' + ', '
		s += 'password:\'' + str(self.password) + '\'' + ', '
		s += 'host:\'' + str(self.host) + '\'' + ', '
		s += 'port:\'' + str(self.port) + '\'' + ', '
		s += Params.dump( self.params, self.kparams )
		s += HParams.dump( self.hparams, self.hkparams )
		s += ']'

		return str(s)

	@nestedproperty
	def hostPort():
		doc = "Host/Port Property"
		def fget( self ):
			if self.port:
				return self.host + ':' + str(self.port)
			else:
				return self.host

		def fset( self, value ):
			n = value.find( ':' )
			if n >= 0:
				self.port = int( value[n+1:] )
				self.host = value[:n]

		return property( fget, fset, None, doc )

	@nestedproperty
	def userPassword():
		doc = "User/Password Property"
		def fget( self ):
			if self.password:
				return self.user + ':' + self.password
			else:
				return self.user

		def fset( self, value ):
			n = value.find( ':' )
			if n >= 0:
				self.password = value[n+1:]
				self.user = value[:n]

		return property( fget, fset, None, doc )

	@nestedproperty
	def allParams():
		doc = "All Parameters Property"
		def fget( self ):
			return buildParams( self.params, self.kparams )

		return property( fget, None, None, doc )

	@nestedproperty
	def allHParams():
		doc = "All HTTP Parameters Property"
		def fget( self ):
			return buildHParams( self.hparams, self.hkparams )

		return property( fget, None, None, doc )

