#!/usr/bin/env python
from mercury.core import SipException
from mercury.header.header import SIP_CRLF
from mercury.message.message import Message
import logging

class StreamReassembler(object):
	def __init__( self ):
		super( StreamReassembler, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )

		self.reset()

	def reset( self ):
		self.message = None
		self.text = ''
		self.contentLength = 0

	def parse( self, text ):
		self.text += text
		self.log.info( 'Parse text:\n' + str(self.text) )

		if not self.message:
			self.log.info( 'No message yet.  Try to find the end of the headers in:\n' + str(self.text) )

			if self.text.isspace():
				self.log.info( 'Ignoring leading whitespace.' )
				self.text = ''
			else:
				# We do not have a any message parsed yet, including just headers.
				n = self.text.find( SIP_CRLF + SIP_CRLF )
				if n >= 0:
					self.log.info( 'Try to parse the headers.' )
					# We have enough to parse the headers.

					# Separate the header from the body.
					headers = self.text[:n+len(SIP_CRLF)+len(SIP_CRLF)]
					self.text = self.text[n:]

					# Try to parse the header.
					try:
						self.message = Message( headers )
					except SipException, e:
						self.log.error( 'Failed to parse the headers: ' + str(e) )
						self.reset()

					if self.message:
						# Get the content length.
						contentLength = self.message['Content-Length']
						if contentLength:
							self.log.info( 'Need content-length of ' + str(contentLength.value) + '.' )
							self.contentLength = contentLength.value

						# Check if this message has a body.
						# Return immediately if it does not.
						if self.contentLength == 0:
							message = self.message
							self.reset()
							return message
				else:
					self.log.info( 'Do not have the end of the headers.' )
					pass

		if self.message:
			if self.contentLength == len(self.text):
				self.log.info( 'Try to parse the body.' )
				try:
					self.message.body = Body( self.message.headers, self.text )

					# Success
					message = self.message
					self.reset()
					return message

				except SipException, e:
					self.log.error( 'Failed to parse the body: ' + str(e) )
					self.reset()

		return None

class DatagramReassembler(object):
	def parse( self, text ):
		if text.isspace():
			#self.log.info( 'Ignoring leading whitespace.' )
			return None

		try:
			return Message( text )
		except SipException, e:
			pass

		return None

