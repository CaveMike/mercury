#!/usr/bin/env python
from copy import copy
from iron.event import Event
from mercury.core import SipException
from mercury.header.element import *
from mercury.header.elements import *
from mercury.header.header import *
from mercury.header.header import SIP_CRLF
from mercury.message.container import *
from mercury.uri.uri import *
from sys import modules
from time import time
from UserString import MutableString

#-------------------------------------------------------------------------------
#FIXME: This table could be based on status family (e.g. 4xx) and method.
responseHeaders = [ 'To', 'From', 'Call-ID', 'CSeq', 'Via' ]

#-------------------------------------------------------------------------------
codeToReason = \
{
	100: 'Trying',
	180: 'Ringing',
	181: 'Call Being Forwarded',
	182: 'Call Queued',
	183: 'Session Progress',
	200: 'OK',
	202: 'Accepted',
	300: 'Multiple Choices',
	301: 'Moved Permanently',
	302: 'Moved Temporarily',
	305: 'Use Proxy',
	380: 'Alternative Service',
	400: 'Bad Request',
	401: 'Unauthorized',
	402: 'Payment Required',
	403: 'Forbidden',
	404: 'Not Found',
	405: 'Method Not Allowed',
	406: 'Not Acceptable',
	407: 'Proxy Authentication Required',
	408: 'Request Timeout',
	409: 'Conflict',
	410: 'Gone',
	411: 'Length Required',
	413: 'Request Entity Too Large',
	414: 'Request URI Too Long',
	415: 'Unsupported Media Type',
	416: 'Unsupported URI Scheme',
	420: 'Bad Extension',
	421: 'Extension Required',
	423: 'Interval Too Brief',
	480: 'Temporarily Unavailable',
	481: 'Call/Transaction Does Not Exist',
	482: 'Loop Detected',
	483: 'Too Many Hops',
	484: 'Address Incomplete',
	485: 'Ambiguous',
	486: 'Busy Here',
	487: 'Request Terminated',
	488: 'Not Acceptable Here',
	491: 'Request Pending',
	493: 'Undecipherable',
	500: 'Server Internal Error',
	501: 'Not Implemented',
	502: 'Bad Gateway',
	503: 'Service Unavailable',
	504: 'Server Time-Out',
	505: 'Version Not Supported',
	513: 'Message Too Large',
	600: 'Busy Everywhere',
	603: 'Declined',
	604: 'Does Not Exist Anywhere',
	606: 'Not Acceptable',
}
reasonToCode = invertDict( codeToReason )

#===============================================================================
class Message(Container):
	"""An abstract factory for Request and Response objects."""

	def __new__( cls, value = None ):
		#print '__new__', str(cls)
		if cls == Message:
			#print '__new__', str(cls), str(value)
			if not value:
				raise SipException( 'Failed to parse an empty message.' )

			# Determine if this is a request or response based on the first line.
			if value.find( 'SIP/' ) == 0:
				#print 'Response'
				return object.__new__( Response, value )
			else:
				#print 'Request'
				return object.__new__( Request, value )
		elif cls == Request or cls == Response:
			#print '__new__', str(cls), str(value)
			# Just build the object.
			return object.__new__(cls)

#===============================================================================
class Request(Message):
	def __init__( self, value = None ):
		# Initialize these variables before calling the super __init__ because
		# the super __init__ will 'lock-down' all sets and require that future
		# sets be made on existing variables only.  See Container.__setattr__.
		self.protocol = 'SIP'
		self.version = '2.0'
		self.method = None
		self.requestUri = None
		super( Request, self ).__init__( value )

	def parse( self, value ):
		if not value:
			raise SipException( 'Failed to parse an empty request.' )

		n = value.find( SIP_CRLF )
		if n < 0:
			raise SipException( 'Failed to find the first line of the request.' )

		first = value[:n] # Leave off the SIP_CRLF from first.
		rest = value[n+len(SIP_CRLF):]
		#self.log.info( 'first: ' + str(first) + '.' )
		#self.log.info( 'rest: ' + str(rest) + '.' )

		self.parseFirstLine( first )
		super( Request, self ).parse( rest )

	def parseFirstLine( self, first ):
		if not first:
			raise SipException( 'Failed to parse the first line of the request , ' + str(first) + '.' )

		n = first.rfind( '/' )
		if n < 0:
			raise SipException( 'Failed to parse the version of the request , ' + str(first) + '.' )
		self.version = first[n+1:]
		first = first[:n]

		n = first.rfind( ' ' )
		if n < 0:
			raise SipException( 'Failed to parse the protocol of the request , ' + str(first) + '.' )
		self.protocol = first[n+1:]
		first = first[:n]

		n = first.find( ' ' )
		if n < 0:
			raise SipException( 'Failed to parse the request-URI of the request , ' + str(first) + '.' )
		self.requestUri = Uri( first[n+1:] )
		self.method = first[:n]

	def build( self ):
		s = MutableString()

		s += self.buildFirstLine()
		s += super( Request, self ).build()

		return str(s)

	def buildFirstLine( self ):
		s = MutableString()

		s += str(self.method)
		s += ' '
		s += str(self.requestUri)
		s += ' '
		s += str(self.protocol)
		s += '/'
		s += str(self.version)
		s += SIP_CRLF

		return str(s)

	def validate( self, thorough = False  ):
		if not method:
			raise SipException( 'Missing method.' )

		if not requestUri:
			raise SipException( 'Missing request URI.' )

		if not protocol:
			raise SipException( 'Missing protocol.' )

		if not version:
			raise SipException( 'Missing version.' )

		if thorough:
			if protocol != 'SIP':
				raise SipException( 'Invalid protocol, ' + str(protocol) + '.' )

			if version != '2.0':
				raise SipException( 'Invalid version, ' + str(version) + '.' )

		super( Request, self ).validate( thorough )

#===============================================================================
class Response(Message):
	def __init__( self, value = None ):
		# Initialize these variables before calling the super __init__ because
		# the super __init__ will 'lock-down' all sets and require that future
		# sets be made on existing variables only.  See Container.__setattr__.
		#print '__init__:', str(value)
		self.protocol = 'SIP'
		self.version = '2.0'
		self.code = None
		self.reason = None
		super( Response, self ).__init__( value )

	def setStatus( self, code, reason = None ):
		if not code:
			code = 200

		if not reason:
			if codeToReason.has_key( code ):
				reason = codeToReason[code]
			else:
				reason = ''

		self.code = code
		self.reason = reason

	@nestedproperty
	def method():
		doc = "Returns the method from this response.  Extracts the method from the CSeq header."
		def fget( self ):
			return self.CSeq.method

		return property( fget, None, None, doc )

	@nestedproperty
	def statusClass():
		doc = "Returns the status-class (or family).  For example, 2 for statuses in the range of 200-299."
		def fget( self ):
			return int( self.code / 100 )

		return property( fget, None, None, doc )

	def parse( self, value ):
		if not value:
			raise SipException( 'Failed to parse an empty response.' )

		n = value.find( SIP_CRLF )
		if n < 0:
			raise SipException( 'Failed to find the first line of the response.' )

		first = value[:n] # Leave off the SIP_CRLF from first.
		rest = value[n+len(SIP_CRLF):]
		#self.log.info( 'first: ' + str(first) + '.' )
		#self.log.info( 'rest: ' + str(rest) + '.' )

		self.parseFirstLine( first )
		super( Response, self ).parse( rest )

	def parseFirstLine( self, first ):
		if not first:
			raise SipException( 'Failed to parse the first line of the response , ' + value + '.' )

		n = first.find( '/' )
		if n < 0:
			raise SipException( 'Failed to parse the protocol of the response , ' + value + '.' )
		self.protocol = first[:n]
		first = first[n+1:]

		n = first.find( ' ' )
		if n < 0:
			raise SipException( 'Failed to parse the version of the response , ' + value + '.' )
		self.version = first[:n]
		first = first[n+1:]

		n = first.find( ' ' )
		if n < 0:
			raise SipException( 'Failed to parse the code of the response , ' + value + '.' )
		self.code = int( first[:n] )
		self.reason = first[n+1:]

	def build( self ):
		s = MutableString()

		s += self.buildFirstLine()
		s += super( Response, self ).build()

		return str(s)

	def buildFirstLine( self ):
		s = MutableString()

		s += str(self.protocol)
		s += '/'
		s += str(self.version)
		s += ' '
		s += str(self.code)
		s += ' '
		s += str(self.reason)
		s += SIP_CRLF

		return str(s)

	def validate( self, thorough = False  ):
		if not protocol:
			raise SipException( 'Missing protocol.' )

		if not version:
			raise SipException( 'Missing version.' )

		if not code:
			raise SipException( 'Missing code.' )

		if not reason:
			raise SipException( 'Missing reason.' )

		if thorough:
			if protocol != 'SIP':
				raise SipException( 'Invalid protocol, ' + str(protocol) + '.' )

			if version != '2.0':
				raise SipException( 'Invalid version, ' + str(version) + '.' )

			if code > 699:
				raise SipException( 'Invalid code, ' + str(code) + '.' )

		super( Response, self ).validate( thorough )

#-------------------------------------------------------------------------------
def createResponse( request, code = None, reason = None ):
	# Create the response.
	response = Response()

	# Copy the status line.
	response.protocol = copy(request.protocol)
	response.version = copy(request.version)
	response.setStatus( code, reason )

	# Copy the appropriate headers.
	for headerName in responseHeaders:
		if request[headerName]:
			response[headerName] = copy(request[headerName])

	return response

#===============================================================================
class MessageEvent(Event):

	EVENT_RX = 'Rx'
	EVENT_TX = 'Tx'

	def __init__( self, id, message, binding = None, connection = None, transport = None, localAddress = None, localPort = None, remoteAddress = None, remotePort = None, useragent = None ):
		super( MessageEvent, self ).__init__( id )
		self.message = message
		self.binding = binding
		self.connection = connection
		#FIXME: really the binding
		self.transport = transport
		self.localAddress = localAddress
		self.localPort = localPort
		#FIXME: really the connection
		self.remoteAddress = remoteAddress
		self.remotePort = remotePort
		self.timestamp = time()
		# Determined as the event is processed.
		self.useragent = None
		self.remoteHost = None
		self.remoteUser = None
		self.localHost = None
		self.localUser = None
		self.dialog = None
		self.transaction = None
		self.request = None
		self.response = None

		if isinstance( message, Request ):
			self.request = message
		elif isinstance( message, Response ):
			self.response = message
		else:
			raise TypeError( 'Invalid message type.' )

		self.id = self.id + self.message.__class__.__name__

	def __str__( self ):
		return '%s, %s(%s:%s %s:%s), messageLength: %s, timestamp: %s, ' \
		'binding: %s, connection: %s, ' \
		'useragent: %s, remoteHost: %s, remoteUser: %s, localHost: %s, localUser: %s, dialog: %s, transaction: %s' \
		% ( Event.__str__(self), str(self.transport), str(self.localAddress), str(self.localPort), str(self.remoteAddress), str(self.remotePort), str(len(self.message)), str(self.timestamp), \
		str(self.binding), str(self.connection), \
		str(self.useragent), str(self.remoteHost), str(self.remoteUser), str(self.localHost), str(self.localUser), str(self.dialog), str(self.transaction) )
		#'useragent: request: %s, response: %s, message: %s' \
		#, str(self.request), str(self.response), str(self.message)

#-------------------------------------------------------------------------------
def createResponseEvent( requestEvent, code = None, reason = None ):
	response = createResponse( requestEvent.message, code, reason )

	if requestEvent.id.startswith( MessageEvent.EVENT_RX ):
		id = MessageEvent.EVENT_TX
	elif requestEvent.id.startswith( MessageEvent.EVENT_TX ):
		id = MessageEvent.EVENT_RX
	else:
		#FIXME:
		print requestEvent.id
		raise 0

	responseEvent = MessageEvent( id, response, requestEvent.binding, requestEvent.connection, requestEvent.transport, requestEvent.localAddress, requestEvent.localPort, requestEvent.remoteAddress, requestEvent.remotePort )
	return responseEvent

