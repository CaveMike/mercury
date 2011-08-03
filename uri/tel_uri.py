#!/usr/bin/env python
from carbon.importer import importExtension
from mercury.header.element import IElement
from mercury.header.element import Params
import logging
import mercury.core
import mercury.header.element
import unittest
from UserString import MutableString

class TelUri(IElement):
	def __init__( self, value = None ):
		super( TelUri, self ).__init__( value )
		self.protocol = None
		self.user = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		try:
			n = value.find( ':' )
			if n < 0:
				raise SipException( 'Failed to parse protocol of URI, ' + value + '.' )
			self.protocol = value[:n]
			value = value[n+1:]

			self.user = Params.parse( self.params, self.kparams, value )

			if not self.user:
				raise SipException( 'Failed to parse user of URI, ' + value + '.' )
		except not SipException:
			raise SipException( 'Failed to parse the URI, ' + value + '.' )


	def build( self ):
		s = MutableString()

		if self.protocol:
			s += self.protocol
			s += ':'

		if not self.user:
			raise SipException( 'User not specified' )

		if self.user:
			s += self.user

		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False ):
		if not self.protocol:
			raise SipException( 'Invalid protocol in URI, ' + str(self) + '.' )

		if not self.user:
			raise SipException( 'Invalid user in URI, ' + str(self) + '.' )

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'protocol:\'' + str(self.protocol) + '\'' + ', '
		s += 'user:\'' + str(self.user) + '\'' + ', '
		s += Params.dump( self.params, self.kparams )
		s += ']'

		return str(s)

