#!/usr/bin/env python
from mercury.body.body import Body

class ApplicationPidfXmlBody(Body):
	def __init__( self, headers, body ):
		super( ApplicationPidfXmlBody, self ).__init__( headers, body )

	def parse( self, value ):
		pass

	def build( self ):
		return ''

	def validate( self, thorough = False  ):
		return True

	def dump( self ):
		return __str__.self()

