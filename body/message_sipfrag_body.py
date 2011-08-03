#!/usr/bin/env python
from mercury.message.message import Message
from mercury.body.body import Body

class MessageSipfragBody(Body):
	def __init__( self, headers, body ):
		super( MessageSipfragBody, self ).__init__( headers, body )
		self.message = None

		if body:
			self.parse( body )

	def parse( self, value ):
		self.message = Message( value )

	def build( self ):
		return self.message.build()

	def validate( self, thorough = False  ):
		return self.message.validate( thorough )

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'message:\'' + str(self.message) + '\'' + ', '
		s += ']'

		return str(s)

