from core import SipException
from event import Event
from carbon.importer import importExtension
from message import *

#===============================================================================
class AuthenticationAdapter(object):
	"""Challenges requests and verifies challenge responses."""

	def __init__( self, proxyAuthentication = False ):
		super( AuthenticationAdapter, self ).__init__()
		self.log = Logger().get_instance( self.__class__.__name__ )

		"""
		Authentication-Info 2xx -  o - o o o
		Authorization       R   o  o o o o o	(challenge response)
		Proxy-Authenticate  407 ar - m - m m m	(challenge request)
		Proxy-Authenticate  401 ar - o o o o o	(challenge request)
		Proxy-Authorization R   dr o o - o o o	(challenge response)
		WWW-Authenticate    401 ar - m - m m m	(challenge request)
		WWW-Authenticate    407 ar - o - o o o	(challenge request)
		"""
		self.proxyAuthentication = proxyAuthentication
		if self.proxyAuthentication:
			self.statusCode = 407
			self.challengeRequestHeader = 'Proxy-Authenticate'
			self.challengeResponseHeader = 'Proxy-Authorization'
		else:
			self.statusCode = 401
			self.challengeRequestHeader = 'WWW-Authenticate'
			self.challengeResponseHeader = 'Authorization'

		self.authentication = None
		obj = importExtension( 'simple_authentication' )
		if obj:
			self.authentication = obj()

	def identifyEvent( self, event ):
		self.log.info( str(event) )

		if isinstance( event, MessageEvent ):
			return event.id
		elif isinstance( event, ResourceEvent ):
			return event.id

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	def onRxRequest( self, event ):
		# Get the challenge response (if available).
		header = event.message[self.challengeResponseHeader]
		if header:
			challengeRequest = self.authentication.verifyChallengeResponse( username=header.username, realm=header.realm, nonce=header.nonce, uri=header.uri, response=header.response, algorithm=header.algorithm, method=event.message.method )
			if challengeRequest:
				# Verification failed.  Send a 401/407 with the the new challenge request.
				pass
		else:
			challengeRequest = self.authentication.createChallengeRequest()

		if challengeRequest:
			# Send the challenge request.
			newEvent = createResponseEvent( event, self.statusCode )

			newEvent.message[self.challengeRequestHeader] = 'Digest '
			header = newEvent.message[self.challengeRequestHeader]
			header.realm = challengeRequest['realm']
			header.domain = challengeRequest['domain']
			header.nonce = challengeRequest['nonce']
			header.stale = 'False'
			header.algorithm = challengeRequest['algorithm']
			newEvent.message[self.challengeRequestHeader] = header

			self.notify( newEvent, queued=True )
		else:
			# Pass the request on.
			pass

	def onRxResponse( self, event ):
		if event.message.code == 401 or event.message.code == 407:
			#FIXME:IMPLEMENT:
                        pass
		else:
			# Pass the response on.
			pass

	def onTxRequest( self, event ):
		self.notify( event, queued=False )

	def onTxResponse( self, event ):
		self.notify( event, queued=False )
