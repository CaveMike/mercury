#!/usr/bin/env python
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
import logging
from mercury.header.header import *
import unittest

class TestRaw(unittest.TestCase):
	def runTest( self ):
		cseq = CSeqHeader()

		try:
			cseq.raw = 'xxxxx'
		except AttributeError:
			pass
		else:
			fail( 'Expected a AttributeError to be raised.' )

		try:
			del cseq.raw
		except AttributeError:
			pass
		else:
			fail( 'Expected a AttributeError to be raised.' )

if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

