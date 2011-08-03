#!/usr/bin/env python
# list
#	Indexed by position.
#	Element doesn't store position.
#	Element stores name.  Name is less likely to change than position.
#	Order is easy to keep valid since it is built-in to the list.
#	Could support multiple headers with the same name.  DO WE WANT TO?
#	Lookup by name requires a list-comprehension.  Slower and more wasteful than dict.
#
# dict
#	Indexed by name.
#	Element doesn't store name.
#	Element stores position.  Position is more likely to change than name.
#	Order struct is hard to keep valid (have to walk through entire order struct to add an entry).
#	Only one header per name.  so comma-headers and multi-headers MUST be combined.
#	Lookup by name is trivial and fast.

# Most common operations:
#	(1)
#	Get header by name from message.
#	(1.5)
#	Change existing header by name.
#	(2)
#	Parse message from string.  Create and insert headers in network order.
#	Create message programatically.  Create and insert headers in programming order.
#	Build message as string.
#	(3)
#	Add header to end of message.
#	(4)
#	Re-order some headers (Via, Route, etc.)
#	(5)
#	Insert header in the middle of a message.
#	Re-order all headers (by sort for example).
#

from mercury.body.body import Body
from copy import copy
from mercury.core import SipException
from mercury.header.element import *
from mercury.header.elements import *
from mercury.header.header import *
from mercury.header.header import SIP_CRLF
from itertools import *
from UserList import UserList
from UserString import MutableString
import unittest
import logging

class SipExceptionIncompleteBody(SipException): pass

class Container(IElement, UserList):
	def __init__( self, value = None ):
		super( Container, self ).__init__( value )
		self.body = None
		self.consolidateHeaders = True
		self.data = []

		if value:
			self.parse( value )

	"""
	Shortcut to get the header element.
		When there are no header elements, returns None.
		When there is exactly one header element, returns it.
		When there are more than one header elements by that name, throws an exception.
	"""
	def __getitem__( self, index ):
		#print '(Get) Item ' + str(index) + '.'
		if isinstance( index, str ):
			pass
		elif isinstance( index, Header ):
			index = index.name
		elif isinstance( index, int ):
			return UserList.__getitem__( self, index )
		else:
			raise SipException( 'Cannot get header, ' + str(index) + ', using type, ' + str(type(index)) + '.' )

		l = [ header for header in self if header.name == index ]
		if len(l) == 0:
			return None
		elif len(l) == 1:
			if len(l[0]) == 0:
				return None
			elif len(l[0]) == 1:
				return l[0][0]

		raise SipException( 'There are more than one headers with the name, ' + str(index) + '.  You must use getHeaders() to get the list of headers.' )

	def getHeaders( self, index ):
		#print '(Get) Item ' + str(index) + '.'
		if isinstance( index, str ):
			pass
		elif isinstance( index, Header ):
			index = index.name
		elif isinstance( index, int ):
			return UserList.__getitem__( self, index )
		else:
			raise SipException( 'Cannot get header, ' + str(index) + ', using type, ' + str(type(index)) + '.' )

		l = [ header for header in self if header.name == index ]
		return l

	def __setitem__( self, name, value ):
		#print '(Set) Item ' + str(name) + ', ' + str(value) + '.'

		if isinstance( name, str ):
			try:
				index = self.index( name )
			except ValueError:
				index = None
		elif isinstance( name, Header ):
			try:
				index = self.index( name.name )
			except ValueError:
				index = None
		elif isinstance( name, int ):
			pass
		else:
			raise SipException( 'Cannot set header, ' + str(name) + ', using type, ' + str(type(index)) + '.' )

		if value is None:
			raise SipException( 'Cannot set header, ' + str(name) + ', to, ' + str(value) + '.  Use del instead.' )

		if index is not None:
			# If this element already exists, then remove it.
			self.pop( index )

		if isinstance( value, str ):
			self.addHeader( name, value, index )
		elif isinstance( value, int ):
			self.addHeader( name, str(value), index ) #FIXME: Probably not Optimal?
		elif isinstance( value, Header ):
			if index is None:
				self.append( value )
			else:
				self.insert( index, value )
		elif isinstance( value, IElement ):
			self.addHeader( name, str(value), index ) #FIXME: Not Optimal.  Header needs a constructor that takes an element.
		else:
			raise SipException( 'Cannot create a header, ' + str(name) + ', using type, ' + str(type(value)) + '.' )

	def __delitem__( self, name ):
		#print '(Del) Item: ' + str(name) + '.'
		if isinstance( name, str ):
			try:
				index = self.index( name )
			except ValueError:
				index = None
		elif isinstance( name, Header ):
			try:
				index = self.index( name.name )
			except ValueError:
				index = None
		elif isinstance( name, int ):
			pass
		else:
			raise SipException( 'Cannot delete header, ' + str(name) + ', using type, ' + str(type(index)) + '.' )

		if index is not None:
			self.pop( index )

	def iterHeaders( self ):
		for header in self:
			# Return the Header object.
			yield header
			for subheader in header:
				# Return the Element object.
				yield subheader

	def iterBodies( self ):
		yield self.body
		for subbody in self.body:
			yield subbody

	# Add
	def append( self, object ):
		if isinstance( object, str ):
			# If the object is passed in as a string, then parse it.
			self.parseHeader( object )
		else:
			super( Container, self ).append( object )

	def insert( self, index, object ):
		if isinstance( object, str ):
			# If the object is passed in as a string, then parse it.
			self.parse( object )
		else:
			super( Container, self ).insert( index, object )

	# IElement
	def parse( self, value ):
		if not value:
			raise SipException( 'Failed to parse an empty message.' )

		n = value.find( SIP_CRLF + SIP_CRLF )
		if n >= 0:
			headers = value[:n+len(SIP_CRLF)]
			body  = value[n+len(SIP_CRLF)+len(SIP_CRLF):]
		else:
			headers = value
			body  = None

		# Parse the headers.
		self.parseHeaders( headers )

		# Parse the body.
		self.parseBody( self, body )

	def parseHeaders( self, value ):
		if not value:
			return

		lines = value.split( SIP_CRLF )

		for i, line in enumerate(lines):
			if not line:
				continue

			self.parseHeader( line )

	def parseHeader( self, value ):
		try:
			(name, element) = value.split( ':', 1 )
			name = name.strip()
			element = element.strip()
			self.addHeader( name, element )
		except ValueError, e:
			raise SipException( 'Cannot parse header, ' + str(value) + '.' )

	def addHeader( self, name, value, index = None ):
		if self.consolidateHeaders:
			l = [ tempHeader for tempHeader in self if tempHeader.name == name ]
			if l is None or len(l) == 0:
				pass
			elif len(l) == 1:
				l[0].appendElement( name, value )
				return
			else:
				raise SipException( 'Adding header, ' + str(name) + ', and consolidateHeaders is ' + str(self.consolidateHeaders) + ', but there is more than one header already present.' )

		header = Header( name, value )
		if index is None:
			self.append( header )
		else:
			self.insert( index, header )

	def parseBody( self, headers, value ):
		if not headers:
			return

		if not value:
			return

		contentLength = headers['Content-Length']
		if contentLength:
			if contentLength.value != len(value):
				raise SipExceptionIncompleteBody( 'The Content-Length, ' + str(contentLength.value) + ', does not match the length of the body, ' + str(len(value)) + '.' )

		self.body = Body( headers, value )

	def build( self ):
		s = MutableString()

		for header in self:
			s += header

		s += SIP_CRLF

		if self.body:
			s += self.body

		return str(s)

	def dump( self ):
		s = MutableString()

		s += '[ '
		for header in self:
			s += header.dump()
			s += ', '
		s += ' ]'

		return str(s)

