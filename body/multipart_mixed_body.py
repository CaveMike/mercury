#!/usr/bin/env python
from mercury.body.body import Body
from mercury.header.header import SIP_CRLF
from mercury.message.container import Container
from UserString import MutableString

class MultipartMixedBody(Body):
	def __init__( self, headers, body ):
		super( MultipartMixedBody, self ).__init__( headers, body )
		contentType = headers['Content-Type']
		self.boundary = contentType.kparams['boundary']
		self.bodies = []

		if body:
			self.parse( body )

	def __iter__( self ):
		for body in self.bodies:
			yield body

	def parse( self, value ):
		bodies = value.split( '--' + self.boundary )
		for body in bodies:
			body = body.lstrip( SIP_CRLF )
			if not body:
				continue

			# If this is the terminating body, then quit.
			if body.startswith( '--' ):
				break

			message = Container( body )

			self.bodies.append( message )

	def build( self ):
		s = MutableString()

		for body in self.bodies:
			s += '--'
			s += self.boundary
			s += SIP_CRLF
			s += body
		s += '--'
		s += self.boundary
		s += '--'
		s += SIP_CRLF

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '

		for ( name, body ) in self.bodies.iteritems():
			s += str(name) + ': ' + '\'' + str(body) + '\'' + ', '

		s += ']'

		return str(s)

