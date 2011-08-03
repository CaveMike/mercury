#!/usr/bin/env python
from carbon.importer import importExtension
from mercury.core import SipException
from mercury.header.element import IElement

class Body(IElement):
	"""An abstract factory for body objects."""

	def __new__( cls, headers, body ):
		if cls == Body:
			contentType = headers['Content-Type']
			name = contentType.fullType + '_body'
			obj = importExtension( name, 'mercury.body' )

			if obj:
				return obj( headers, body )

			raise SipException( 'Cannot create body, ' + contentType.fullType + '.' )
		else:
			# Just build the object.
			return object.__new__( cls, headers, body )

	def __init__( self, headers, body ):
		super( Body, self ).__init__( body )

	def __iter__( self ):
		raise StopIteration

