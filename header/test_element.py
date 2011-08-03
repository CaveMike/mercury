#!/usr/bin/env python
from copy import copy
from mercury.core import SipException
from carbon.helpers import nestedproperty
from UserString import MutableString
import logging
import unittest
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
from mercury.header.header import *
from time import gmtime

class Test(unittest.TestCase):
	def runTest( self ):

		e = IElement()
		self.assertRaises( SipException, e.parse, '12 INVITE' )

		header = WWWAuthenticateHeader( 'Digest realm="sip:sip.example.com", domain="ericsson.com", nonce="x", stale=FALSE, algorithm=MD5' )
		header.realm = 'hi'
		header.domain = 'dom'
		header.algorithm = 'algo'
		header.stale = 'staley'
		header.qop = 'qopy'
		header.nonce = 'xxdfsdfsadf'
		#print header

		header = AuthorizationHeader( 'Digest username="1",realm="sip:sip.example.com",nonce="x",uri="sip:sip.example.com",response="076948a9fe1c3a01a943df47841e1e08",algorithm=md5' )
		#print header

		header = DateHeader()
		#print header
		header = DateHeader( 'Fri, 13 Jul 1971 23:40:12 GMT' )
		#print header
		header.time = gmtime()
		#print header
		#print str(header.time)
		#print str(header.dump())

if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()
