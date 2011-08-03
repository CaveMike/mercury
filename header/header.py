#!/usr/bin/env python
from copy import copy
from carbon.helpers import invertDict
from carbon.importer import makeIdentifier
from itertools import *
from mercury.core import SipException
from mercury.header.element import IElement
from mercury.header.elements import Address
from mercury.header.elements import InfoElement
from mercury.header.elements import CSeq
from mercury.header.elements import Via
from mercury.header.elements import StringElement
from mercury.header.elements import NumericElement
from mercury.header.elements import ContentType
from mercury.header.elements import MessageCount
from mercury.header.elements import WarningElement
from mercury.header.elements import ChallengeElement
from mercury.header.elements import CredentialsElement
from mercury.header.elements import AuthInfoElement
from mercury.header.elements import DateElement
from mercury.header.elements import LanguageElement
from mercury.header.elements import TimestampElement
from mercury.header.elements import CallIDElement
from mercury.header.elements import EncodingElement
from mercury.uri.uri import Uri
from sys import modules
from UserString import MutableString

#-------------------------------------------------------------------------------
SIP_CRLF = '\r\n'

#-------------------------------------------------------------------------------
longToCompact = \
{
	'Call-ID'          : 'i',
	'Contact'          : 'm',
	'Content-Encoding' : 'e',
	'Content-Length'   : 'l',
	'Content-Type'     : 'c',
	'From'             : 'f',
	'Subject'          : 's',
	'Supported'        : 'k',
	'To'               : 't',
	'Via'              : 'v',
}
compactToLong = invertDict( longToCompact )

#-------------------------------------------------------------------------------
embeddedCommas = \
[
	'Authorization',
	'Proxy-Authenticate',
	'Proxy-Authorization',
	'WWW-Authenticate',
]

#===============================================================================
class Header(IElement, list):
	def __init__( self, name, value = None ):
		super( Header, self ).__init__( value )
		self.name = name
		self.useCompact = False
		self.useCommas = False
		self.embeddedCommas = False

		if value is not None:
			self.parse( name, value )

	def __cmp__( self, other ):
		#FIXME: Comparing with a string only?
		return self.name.__ne__( other )

	# Add
	def append( self, object ):
		if isinstance( object, str ):
			# If the object is passed in as a string, then parse it into a element object.
			object = Element( self.name, object )

		super( Header, self ).append( object )

	def insert( self, index, object ):
		if isinstance( object, str ):
			# If the object is passed in as a string, then parse it into a element object.
			object = Element( self.name, object )

		super( Header, self ).insert( index, object )

	# IElement
	def parse( self, name, value ):
		if value is None:
			raise SipException( 'Failed to parse an empty header.' )

		self.name = name
		if len(self.name) == 1:
			self.useCompact = True
			self.name = compactToLong[ self.name ]

		self.embeddedCommas = self.name in embeddedCommas

		n = value.find( ',' )
		if n >= 0 and not self.embeddedCommas:
			self.useCommas = True

			elements = value.split( ',' )
			for element in elements:
				element = element.strip()
				if not element:
					continue

				self.appendElement( self.name, element )
		else:
			self.appendElement( self.name, value )

	def appendElement( self, name, value ):
		self.append( Element( name, value ) )

	def build( self ):
		s = MutableString()

		if self.useCompact:
			if longToCompact.has_key( self.name ):
				self.name = longToCompact[self.name]

		if self.useCommas and not self.embeddedCommas:
			s += self.name
			s += ': '
			s += ','.join( [ str(value) for value in self ] )
			s += SIP_CRLF
		else:
			for value in self:
				s += self.name
				s += ': '
				s += value
				s += SIP_CRLF

		return str(s)

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'name:\'' + str(self.name) + '\'' + ', '
		s += 'useCompact:\'' + str(self.useCompact) + '\'' + ', '
		s += 'useCommas:\'' + str(self.useCommas) + '\'' + ', '
		s += 'embeddedCommas:\'' + str(self.embeddedCommas) + '\'' + ', '
		s += 'values:\'' + list.__repr__( self ) + '\'' + ', '
		s += ']'

		return str(s)

#===============================================================================
class Element(type):
	def __new__( cls, name, value, defaultHeader = 'StringElement' ):
		if cls == Element:
			# Validate the input parameters.
			if not name:
				raise SipException( 'Cannot create header, ' + str(name) + '.' )

			if value is None:
				raise SipException( 'Cannot create header, ' + str(name) + ' with value, '+ str(value) + '.' )

			# Try to find the class type.
			clsName = makeIdentifier( name ) + 'Header'
			if hasattr( modules[__name__], clsName ):
				obj = getattr( modules[__name__], clsName )
			elif defaultHeader:
				obj = getattr( modules[__name__], defaultHeader )
			else:
				obj = None

			# Create the object if the class type is available.
			if obj:
				return obj( value )
			else:
				raise SipException( 'Cannot create header, ' + str(name) + '.  Header object not known.' )
		else:
			return object.__new__( cls, value )

#===============================================================================
# RFC 3261 (SIP)
class AcceptHeader(ContentType):                    pass
class AcceptEncodingHeader(EncodingElement):        pass
class AcceptLanguageHeader(LanguageElement):        pass
class AlertInfoHeader(InfoElement):                 pass
class AllowHeader(StringElement):                   pass
class AuthenticationInfoHeader(AuthInfoElement):    pass
class AuthorizationHeader(CredentialsElement):      pass
class CallIDHeader(CallIDElement):                  pass
class CallInfoHeader(InfoElement):                  pass
class ContactHeader(Address):                       pass
class ContentDispositionHeader(StringElement):      pass
class ContentEncodingHeader(EncodingElement):       pass
class ContentLanguageHeader(LanguageElement):       pass
class ContentLengthHeader(NumericElement):          pass
class ContentTypeHeader(ContentType):               pass
class CSeqHeader(CSeq):                             pass
class DateHeader(DateElement):                      pass
class ErrorInfoHeader(InfoElement):                 pass
class ExpiresHeader(StringElement):                 pass
class FromHeader(Address):                          pass
class InReplyToHeader(CallIDElement):               pass
class MaxForwardsHeader(NumericElement):            pass
class MinExpiresHeader(NumericElement):             pass
class MIMEVersionHeader(NumericElement):            pass
class OrganizationHeader(StringElement):            pass
class PriorityHeader(StringElement):                pass
class ProxyAuthenticateHeader(ChallengeElement):    pass
class ProxyAuthorizationHeader(CredentialsElement): pass
class ProxyRequireHeader(StringElement):            pass
class RecordRouteHeader(Address):                   pass
class ReplyToHeader(Address):                       pass
class RequireHeader(StringElement):                 pass
class RetryAfterHeader(NumericElement):             pass #FIXME: number, comment, params
class RouteHeader(Address):                         pass
class ServerHeader(ContentType):                    pass
class SubjectHeader(StringElement):                 pass
class SupportedHeader(StringElement):               pass
class TimestampHeader(TimestampElement):            pass
class ToHeader(Address):                            pass
class UnsupportedHeader(StringElement):             pass
class UserAgentHeader(ContentType):                 pass
class ViaHeader(Via):                               pass
class WarningHeader(WarningElement):                pass
class WWWAuthenticateHeader(ChallengeElement):      pass

# RFC 3265 (Subscribe-Notify)
class EventElement(StringElement):             pass
class AllowEventsHeader(EventElement):         pass
class EventHeader(EventElement):               pass
class SubscriptionStateHeader(StringElement):  pass

# RFC 3842 (MWI)
class MessageAccountHeader(Uri):               pass
class MessagesWaitingHeader(StringElement):    pass
class VoiceMessageHeader(MessageCount):        pass
class FaxMessageHeader(MessageCount):          pass
class PagerMessageHeader(MessageCount):        pass
class MultimediaMessageHeader(MessageCount):   pass
class TextMessageHeader(MessageCount):         pass

