#!/usr/bin/env python
from carbon.helpers import containsWhitespace
from carbon.importer import importExtension
from carbon.helpers import nestedproperty
from mercury.core import SipException
from mercury.uri.sip_uri import SipUri
import logging
import unittest

class Uri(type):
	def __new__( cls, value = None ):
		if not value:
			raise SipException( 'Failed to parse empty protocol of URI.' )

		value = value.strip()
		if containsWhitespace( value ):
			raise SipException( 'Whitespace present in URI, ' + str(value) + '.' )

		n = value.find( ':' )
		if n < 0:
			raise SipException( 'Failed to parse protocol of URI, ' + str(value) + '.' )

		protocol = value[:n]

		#print protocol.capitalize() + '-Uri'
		obj = importExtension( protocol.capitalize() + '-Uri', 'mercury.uri' )
		if obj:
			return obj( value )

		raise SipException( 'Cannot create URI, ' + str(value) + '.' )

