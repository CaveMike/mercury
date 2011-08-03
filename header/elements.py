#!/usr/bin/env python
from carbon.helpers import nestedproperty
from UserString import MutableString
from mercury.core import SipException
from mercury.header.element import IElement
from mercury.header.element import Params
from mercury.uri.uri import Uri
import logging

#===============================================================================
class Address(IElement):
	def __init__( self, value = None ):
		super( Address, self ).__init__( value )
		self.name =	None
		self.uri = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
		if self.name != other.name:
			return self.name.__cmp__( other.name )

		if self.uri != other.uri:
			return self.uri.__cmp__( other.uri )

#FIXME:DEBUG:		return super( Address, self ).__cmp__( other )

		n = Params.__cmp__( self.params, self.kparams, other.params, other.kparams )
		if n != 0:
			return n

		return 0

	def parse( self, value ):
		name = None
		uri = None

		# Try to parse using angle-brackets.
		n = value.find( '>' )
		if n >= 0:
			dummy = Params.parse( self.params, self.kparams, value[n+1:] )

			nameUri = value[:n]
			n = nameUri.find( '<' )
			if n < 0:
				raise SipException( 'Failed to find the matching left-angle-bracket for address, ' + value + '.' )

			uri = nameUri[n+1:]
			name = nameUri[:n]
		else:
			nameUri = Params.parse( self.params, self.kparams, value )

			uriIndex = 0
			nameUriArray = nameUri.split( '"' )
			if len(nameUriArray) == 1:
				pass
			elif len(nameUriArray) == 3:
				name = nameUriArray[1]
				uriIndex = 2
			else:
				raise SipException( 'Failed to parse address, ' + value + '.' )

			uri = nameUriArray[uriIndex]

		# Display Name
		if name:
			name = name.strip( ' ' )
			self.name = name.strip( '"' )

		# URI
		if uri:
			self.uri = Uri( uri )
		else:
			raise SipException( 'Failed to find URI in address, ' + value + '.' )

	def build( self ):
		s = MutableString()

		if self.name:
			s += '"'
			s += self.name
			s += '"'

		if self.uri:
			s += '<'
			s += str(self.uri)
			s += '>'

		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False  ):
		self.uri.validate( thorough )

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'name:\'' + str(self.name) + '\'' + ', '
		s += 'uri:\'' + str(self.uri) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class InfoElement(IElement):
	def __init__( self, value = None ):
		super( InfoElement, self ).__init__( value )
		self.uri = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
		if self.uri != other.uri:
			return self.uri.__cmp__( other.uri )

		n = Params.__cmp__( self.params, self.kparams, other.params, other.kparams )
		if n != 0:
			return n

		return 0

	def parse( self, value ):
		lvalue = Params.parse( self.params, self.kparams, value )
		if lvalue.startswith( '<' ) and lvalue.endswith( '>' ):
			lvalue = lvalue.lstrip( '<' )
			lvalue = lvalue.rstrip( '>' )
			self.uri = Uri( uri )
		else:
			SipException( 'InfoElement, ' + str(self.value) + ', does not have opening or closing brackets.' )

	def build( self ):
		s = MutableString()

		if self.uri:
			s += '<'
			s += str(self.uri)
			s += '>'

		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False  ):
		self.uri.validate( thorough )

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'uri:\'' + str(self.uri) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class CSeq(IElement):
	def __init__( self, value = None ):
		super( CSeq, self ).__init__( value )
		self.value = None
		self.method = None
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
		if self.value != other.value:
			return self.value.__cmp__( other.value )

		if self.method != other.method:
			return self.method.__cmp__( other.method )

		return 0

	def parse( self, value ):
		if value:
			(self.value, self.method ) = value.split( ' ', 1 )
			self.value = int(self.value)

	def build( self ):
		s = MutableString()

		s += str(self.value)
		s += ' '
		s += str(self.method)

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'value:\'' + str(self.value) + '\'' + ', '
		s += 'method:\'' + str(self.method) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class Via(IElement):
	def __init__( self, value = None ):
		super( Via, self ).__init__( value )
		self.protocol = None
		self.version = None
		self.transport = None
		self.host = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
		if self.protocol != other.protocol:
			return self.protocol.__cmp__( other.protocol )

		if self.version != other.version:
			return self.version.__cmp__( other.version )

		if self.transport != other.transport:
			return self.transport.__cmp__( other.transport )

		if self.host != other.host:
			return self.host.__cmp__( other.host )

		n = Params.__cmp__( self.params, self.kparams, other.params, other.kparams )
		if n != 0:
			return n

		return 0

	def parse( self, value ):
		value = Params.parse( self.params, self.kparams, value )
		if value:
			values = value.split( ' ' )
			self.host = values[1]

			values = values[0].split( '/' )
			self.protocol  = values[0]
			self.version   = values[1]
			self.transport = values[2]

	def build( self ):
		s = MutableString()

		s += self.protocol
		s += '/'
		s += self.version
		s += '/'
		s += self.transport
		s += ' '
		s += str(self.host)

		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'protocol:\'' + str(self.protocol) + '\'' + ', '
		s += 'version:\'' + str(self.version) + '\'' + ', '
		s += 'transport:\'' + str(self.transport) + '\'' + ', '
		s += 'host:\'' + str(self.host) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class StringElement(IElement):
	def __init__( self, value = None ):
		super( StringElement, self ).__init__( value )
		self.value = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
#FIXME: Other __cmp__ must handler other=None
		if not other:
			return 0

		if self.value != other.value:
			return self.value.__cmp__( other.value )

		n = Params.__cmp__( self.params, self.kparams, other.params, other.kparams )
#FIXME: Why this check here and in other cases?
		if n != 0:
			return n

		return 0

	def parse( self, value ):
		value = Params.parse( self.params, self.kparams, value )
		if value:
			self.value = value
		else:
			self.value = ''

	def build( self ):
		s = MutableString()

		s += str(self.value)
		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'value:\'' + str(self.value) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class NumericElement(IElement):
	def __init__( self, value = None ):
		super( NumericElement, self ).__init__( value )
		self.value = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def __cmp__( self, other ):
		if self.value != other.value:
			return self.value.__cmp__( other.value )

		n = Params.__cmp__( self.params, self.kparams, other.params, other.kparams )
		if n != 0:
			return n

		return 0

	def parse( self, value ):
		if ( isinstance( value, int ) ):
			self.value = int(value)
		else:
			value = Params.parse( self.params, self.kparams, value )
			self.value = int(value)

	def build( self ):
		s = MutableString()

		s += str(self.value)
		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'value:\'' + str(self.value) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class ContentType(IElement):
	def __init__( self, value = None ):
		super( ContentType, self ).__init__( value )
		self.type = None
		self.subtype = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		value = Params.parse( self.params, self.kparams, value )
		if value:
			n = value.find( '/' )
			if n >= 0:
				self.type = value[:n]
				self.subtype = value[n+1:]
			else:
				self.type = value

	def build( self ):
		s = MutableString()

		if self.type:
			s += self.type

		if self.subtype:
			s += '/'
			s += str(self.subtype)

		s += Params.build( self.params, self.kparams )

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'type:\'' + str(self.type) + '\'' + ', '
		s += 'subtype:\'' + str(self.subtype) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

	@nestedproperty
	def fullType():
		doc = "Type/Subtype Property"
		def fget( self ):
			if self.subtype:
				return self.type + '/' + str(self.subtype)
			else:
				return self.type

		def fset( self, value ):
			n = value.find( '/' )
			if n >= 0:
				self.subtype = int( value[n+1:] )
				self.type = value[:n]

		return property( fget, fset, None, doc )

#===============================================================================
class MessageCount(IElement):
	def __init__( self, value = None ):
		super( MessageCount, self ).__init__( value )
		self.normal_new = 0
		self.normal_old = 0
		self.urgent_new = 0
		self.urgent_old = 0
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		normal = value
		urgent = None

		n = value.find( '(' )
		if n >= 0:
			normal = value[:n]
			urgent = value[n+1:]
			urgent = urgent.rstrip( ')' )

		if normal:
			n = normal.find( '/' )
			if n >= 0:
				normal_new = int( normal[:n] )
				normal_old = int( normal[n+1:] )
			else:
				normal_new = int( normal )
				normal_old = None

		if urgent:
			n = urgent.find( '/' )
			if n >= 0:
				urgent_new = int( urgent[:n] )
				urgent_old = int( urgent[n+1:] )
			else:
				urgent_new = int( urgent )
				urgent_old = None

	def build( self ):
		s = MutableString()
		s += ( '%d/%d(%d/%d)' % ( self.normal_new, self.normal_old, self.urgent_new, self.urgent_old ) )
		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'normal_new:\'' + str(self.normal_new) + '\'' + ', '
		s += 'noirmal_old:\'' + str(self.noirmal_old) + '\'' + ', '
		s += 'urgent_new:\'' + str(self.urgent_new) + '\'' + ', '
		s += 'urgent_old:\'' + str(self.urgent_old) + '\'' + ', '
		s += ']'

		return str(s)

	@nestedproperty
	def fullType():
		doc = "Type/Subtype Property"
		def fget( self ):
			if self.subtype:
				return self.type + '/' + str(self.subtype)
			else:
				return self.type

		def fset( self, value ):
			n = value.find( '/' )
			if n >= 0:
				self.subtype = int( value[n+1:] )
				self.type = value[:n]

		return property( fget, fset, None, doc )

#===============================================================================
"""
warning-value  =  warn-code SP warn-agent SP warn-text
warn-code      =  3DIGIT
warn-agent     =  hostport / pseudonym
                  ;  the name or pseudonym of the server adding
                  ;  the Warning header, for use in debugging
warn-text      =  quoted-string
pseudonym      =  token
"""
class WarningElement(IElement):
	def __init__( self, value = None ):
		super( WarningElement, self ).__init__( value )
		self.code = None
		self.agent = None
		self.text = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		#FIXME:IMPLEMENT:
		pass

	def build( self ):
		s = MutableString()

		if self.code is not None:
			s += str(self.code)
			s += ' '

		if self.agent:
			s += self.agent
			s += ' '

		if self.text:
			s += '"'
			s += self.text
			s += '"'

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'code:\'' + str(self.code) + '\'' + ', '
		s += 'agent:\'' + str(self.agent) + '\'' + ', '
		s += 'text:\'' + str(self.text) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
"""
challenge           =  ("Digest" LWS digest-cln *(COMMA digest-cln))
                       / other-challenge
other-challenge     =  auth-scheme LWS auth-param
                       *(COMMA auth-param)
digest-cln          =  realm / domain / nonce
                        / opaque / stale / algorithm
                        / qop-options / auth-param
realm               =  "realm" EQUAL realm-value
realm-value         =  quoted-string
domain              =  "domain" EQUAL LDQUOT URI
                       *( 1*SP URI ) RDQUOT
URI                 =  absoluteURI / abs-path
nonce               =  "nonce" EQUAL nonce-value
nonce-value         =  quoted-string
opaque              =  "opaque" EQUAL quoted-string
stale               =  "stale" EQUAL ( "true" / "false" )
algorithm           =  "algorithm" EQUAL ( "MD5" / "MD5-sess"
                       / token )
qop-options         =  "qop" EQUAL LDQUOT qop-value
                       *("," qop-value) RDQUOT
qop-value           =  "auth" / "auth-int" / token
auth-param        =  auth-param-name EQUAL
                     ( token / quoted-string )
auth-param-name   =  token
other-response    =  auth-scheme LWS auth-param
                     *(COMMA auth-param)
"""
class ChallengeElement(IElement):
	def __init__( self, value = None ):
		super( ChallengeElement, self ).__init__( value )
		self.realm = None
		self.domain = None
		self.nonce = None
		self.opaque = None
		self.stale = None
		self.algorithm = None
		self.qop = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		n = value.find( 'Digest ' )
		if n != 0:
			raise SipException( 'Credentials must start with Digest, ' + value + '.' )

		value = value[7:]

		allparams = value.split( ',' )
		for param in allparams:
			n = param.find( '=' )
			if n >= 0:
				v = param[n+1:].strip().strip('"')
				k = param[:n].strip()
				self.kparams[k] = v
			else:
				self.params.append( param.strip() )


		# Extract known parameters.
		if self.kparams.has_key('realm'):
			self.realm = self.kparams['realm']
			del self.kparams['realm']

		if self.kparams.has_key('domain'):
			self.domain = self.kparams['domain']
			del self.kparams['domain']

		if self.kparams.has_key('nonce'):
			self.nonce = self.kparams['nonce']
			del self.kparams['nonce']

		if self.kparams.has_key('opaque'):
			self.opaque = self.kparams['opaque']
			del self.kparams['opaque']

		if self.kparams.has_key('stale'):
			self.stale = self.kparams['stale']
			del self.kparams['stale']

		if self.kparams.has_key('algorithm'):
			self.algorithm = self.kparams['algorithm']
			del self.kparams['algorithm']

		if self.kparams.has_key('qop'):
			self.qop = self.kparams['qop']
			del self.kparams['qop']

	def build( self ):
		s = MutableString()

		s += 'Digest '

		if self.realm:
			s += 'realm="'
			s += self.realm
			s += '",'

		if self.domain:
			s += 'domain="'
			s += self.domain
			s += '",'

		if self.nonce:
			s += 'nonce="'
			s += self.nonce
			s += '",'

		if self.opaque:
			s += 'opaque="'
			s += self.opaque
			s += '",'

		if self.stale is not None:
			s += 'stale='
			if self.stale:
				s += 'true'
			else:
				s += 'false'
			s += ','

		if self.algorithm:
			s += 'algorithm='
			s += self.algorithm
			s += ','

		if self.qop:
			s += 'qop="'
			s += self.qop
			s += '",'

		#for v in self.params:
		#	s += v
		#	s += ', '

		for (k, v) in self.kparams.iteritems():
			s += k
			s += '="'
			s += v
			s += '",'

		return str(s).rstrip(',')

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'realm:\'' + str(self.realm) + '\'' + ', '
		s += 'domain:\'' + str(self.domain) + '\'' + ', '
		s += 'nonce:\'' + str(self.nonce) + '\'' + ', '
		s += 'opaque:\'' + str(self.opaque) + '\'' + ', '
		s += 'stale:\'' + str(self.stale) + '\'' + ', '
		s += 'algorithm:\'' + str(self.algorithm) + '\'' + ', '
		s += 'qop:\'' + str(self.qop) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
"""
credentials       =  ("Digest" LWS digest-response)
                     / other-response
digest-response   =  dig-resp *(COMMA dig-resp)
dig-resp          =  username / realm / nonce / digest-uri
                      / dresponse / algorithm / cnonce
                      / opaque / message-qop
                      / nonce-count / auth-param
username          =  "username" EQUAL username-value
username-value    =  quoted-string
digest-uri        =  "uri" EQUAL LDQUOT digest-uri-value RDQUOT
digest-uri-value  =  rquest-uri ; Equal to request-uri as specified
                     by HTTP/1.1
message-qop       =  "qop" EQUAL qop-value

cnonce            =  "cnonce" EQUAL cnonce-value
cnonce-value      =  nonce-value
nonce-count       =  "nc" EQUAL nc-value
nc-value          =  8LHEX
dresponse         =  "response" EQUAL request-digest
request-digest    =  LDQUOT 32LHEX RDQUOT
auth-param        =  auth-param-name EQUAL
                     ( token / quoted-string )
auth-param-name   =  token
other-response    =  auth-scheme LWS auth-param
                     *(COMMA auth-param)
auth-scheme       =  token
"""
class CredentialsElement(IElement):
	def __init__( self, value = None ):
		super( CredentialsElement, self ).__init__( value )
		self.username = None
		self.realm = None
		self.nonce = None
		self.uri = None
		self.response = None
		self.algorithm = None
		self.cnonce = None
		self.opaque = None
		self.qop = None
		self.nc = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		n = value.find( 'Digest ' )
		if n != 0:
			raise SipException( 'Credentials must start with Digest, ' + value + '.' )

		value = value[7:]

		allparams = value.split( ',' )
		for param in allparams:
			n = param.find( '=' )
			if n >= 0:
				v = param[n+1:].strip().strip('"')
				k = param[:n].strip()
				self.kparams[k] = v
			else:
				self.params.append( param.strip() )


		# Extract known parameters.
		if self.kparams.has_key('username'):
			self.username = self.kparams['username']
			del self.kparams['username']

		if self.kparams.has_key('realm'):
			self.realm = self.kparams['realm']
			del self.kparams['realm']

		if self.kparams.has_key('nonce'):
			self.nonce = self.kparams['nonce']
			del self.kparams['nonce']

		if self.kparams.has_key('uri'):
			self.uri = self.kparams['uri']
			del self.kparams['uri']

		if self.kparams.has_key('response'):
			self.response = self.kparams['response']
			del self.kparams['response']

		if self.kparams.has_key('algorithm'):
			self.algorithm = self.kparams['algorithm']
			del self.kparams['algorithm']

		if self.kparams.has_key('cnonce'):
			self.cnonce = self.kparams['cnonce']
			del self.kparams['cnonce']

		if self.kparams.has_key('opaque'):
			self.opaque = self.kparams['opaque']
			del self.kparams['opaque']

		if self.kparams.has_key('qop'):
			self.qop = self.kparams['qop']
			del self.kparams['qop']

		if self.kparams.has_key('nc'):
			self.nc = self.kparams['nc']
			del self.kparams['nc']

	def build( self ):
		s = MutableString()

		s += 'Digest '

		if self.username:
			s += 'username="'
			s += self.username
			s += '",'

		if self.realm:
			s += 'realm="'
			s += self.realm
			s += '",'

		if self.nonce:
			s += 'nonce="'
			s += self.nonce
			s += '",'

		if self.uri:
			s += 'uri="'
			s += self.uri
			s += '",'

		if self.response:
			s += 'response="'
			s += self.response
			s += '",'

		if self.algorithm:
			s += 'algorithm='
			s += self.algorithm
			s += ','

		if self.cnonce:
			s += 'cnonce="'
			s += self.cnonce
			s += '",'

		if self.opaque:
			s += 'opaque="'
			s += self.opaque
			s += '",'

		if self.qop:
			s += 'qop="'
			s += self.qop
			s += '",'

		if self.nc:
			s += 'nc="'
			s += self.nc
			s += '",'

		#for v in self.params:
		#	s += v
		#	s += ', '

		for (k, v) in self.kparams.iteritems():
			s += k
			s += '="'
			s += v
			s += '",'

		return str(s).rstrip(',')

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'username:\'' + str(self.username) + '\'' + ', '
		s += 'realm:\'' + str(self.realm) + '\'' + ', '
		s += 'nonce:\'' + str(self.nonce) + '\'' + ', '
		s += 'uri:\'' + str(self.uri) + '\'' + ', '
		s += 'response:\'' + str(self.response) + '\'' + ', '
		s += 'algorithm:\'' + str(self.algorithm) + '\'' + ', '
		s += 'cnonce:\'' + str(self.cnonce) + '\'' + ', '
		s += 'opaque:\'' + str(self.opaque) + '\'' + ', '
		s += 'qop:\'' + str(self.qop) + '\'' + ', '
		s += 'nc:\'' + str(self.nc) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
"""
Authentication-Info  =  "Authentication-Info" HCOLON ainfo
                        *(COMMA ainfo)
ainfo                =  nextnonce / message-qop
                         / response-auth / cnonce
                         / nonce-count
nextnonce            =  "nextnonce" EQUAL nonce-value
response-auth        =  "rspauth" EQUAL response-digest
response-digest      =  LDQUOT *LHEX RDQUOT
"""
class AuthInfoElement(IElement):
	def __init__( self, value = None ):
		super( AuthInfoElement, self ).__init__( value )
		self.nextnonce = None
		self.qop = None
		self.rspauth = None
		self.cnonce = None
		self.nc = None
		self.params = []
		self.kparams = {}
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		allparams = value.split( ',' )
		for param in allparams:
			n = param.find( '=' )
			if n >= 0:
				v = param[n+1:].strip().strip('"')
				k = param[:n].strip()
				self.kparams[k] = v
			else:
				self.params.append( param.strip() )


		# Extract known parameters.
		if self.kparams.has_key('nextnonce'):
			self.username = self.kparams['nextnonce']
			del self.kparams['nextnonce']

		if self.kparams.has_key('qop'):
			self.qop = self.kparams['qop']
			del self.kparams['qop']

		if self.kparams.has_key('rspauth'):
			self.realm = self.kparams['rspauth']
			del self.kparams['rspauth']

		if self.kparams.has_key('nonce'):
			self.nonce = self.kparams['nonce']
			del self.kparams['nonce']

		if self.kparams.has_key('nc'):
			self.nc = self.kparams['nc']
			del self.kparams['nc']

	def build( self ):
		s = MutableString()

		if self.nextnonce:
			s += 'nextnonce="'
			s += self.nextnonce
			s += '",'

		if self.qop:
			s += 'qop="'
			s += self.qop
			s += '",'

		if self.rspauth:
			s += 'rspauth="'
			s += self.rspauth
			s += '",'

		if self.cnonce:
			s += 'cnonce="'
			s += self.cnonce
			s += '",'

		if self.nc:
			s += 'nc="'
			s += self.nc
			s += '",'

		#for v in self.params:
		#	s += v
		#	s += ', '

		for (k, v) in self.kparams.iteritems():
			s += k
			s += '="'
			s += v
			s += '",'

		return str(s).rstrip(',')

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'nextnonce:\'' + str(self.nextnonce) + '\'' + ', '
		s += 'qop:\'' + str(self.qop) + '\'' + ', '
		s += 'rspauth:\'' + str(self.rspauth) + '\'' + ', '
		s += 'cnonce:\'' + str(self.cnonce) + '\'' + ', '
		s += 'nc:\'' + str(self.nc) + '\'' + ', '
		s += 'params:\'' + str(self.params) + '\'' + ', '
		s += 'kparams:\'' + str(self.kparams) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
"""
Date          =  "Date" HCOLON SIP-date
SIP-date      =  rfc1123-date
rfc1123-date  =  wkday "," SP date1 SP time SP "GMT"
date1         =  2DIGIT SP month SP 4DIGIT
                 ; day month year (e.g., 02 Jun 1982)
time          =  2DIGIT ":" 2DIGIT ":" 2DIGIT
                 ; 00:00:00 - 23:59:59
wkday         =  "Mon" / "Tue" / "Wed"
                 / "Thu" / "Fri" / "Sat" / "Sun"
month         =  "Jan" / "Feb" / "Mar" / "Apr"
                 / "May" / "Jun" / "Jul" / "Aug"
                 / "Sep" / "Oct" / "Nov" / "Dec"
"""
from time import strptime
from time import strftime
from time import gmtime

class DateElement(IElement):
	def __init__( self, value = None ):
		super( DateElement, self ).__init__( value )
		self.time = None
		self.__dict__['__initialized'] = True

		if value:
			self.parse( value )

	def parse( self, value ):
		self.time = strptime( value, '%a, %d %b %Y %H:%M:%S %Z' )

	def build( self ):
		if not self.time:
			return ''
		else:
			return strftime( '%a, %d %b %Y %H:%M:%S GMT', self.time )

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'time:\'' + str(self.time) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
"""
language         =  language-range *(SEMI accept-param)
language-range   =  ( ( 1*8ALPHA *( "-" 1*8ALPHA ) ) / "*" )
accept-param   =  ("q" EQUAL qvalue) / generic-param
qvalue         =  ( "0" [ "." 0*3DIGIT ] )
                  / ( "1" [ "." 0*3("0") ] )
generic-param  =  token [ EQUAL gen-value ]
gen-value      =  token / host / quoted-string
"""
class LanguageElement(StringElement):
	pass

#===============================================================================
"""
Timestamp  =  "Timestamp" HCOLON 1*(DIGIT)
               [ "." *(DIGIT) ] [ LWS delay ]
delay      =  *(DIGIT) [ "." *(DIGIT) ]
(e.g. n.n n.n (all optional))
"""
class TimestampElement(StringElement):
	pass

#===============================================================================
# These elements are simple element types.
# However, since they are used in multiple headers, give them a common parent.
class CallIDElement(StringElement):   pass
class EncodingElement(StringElement): pass

