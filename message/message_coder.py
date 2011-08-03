#!/usr/bin/env python
import logging

class MessageCoder(object):
	def __init__( self, coding = 'utf_8' ):
		super( MessageCoder, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )

		self.coding = coding

	def decode( self, packet ):
		return str( packet ).decode( self.coding )

	def encode( self, message ):
		return str( message ).encode( self.coding )

