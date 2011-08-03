import digest as Digest

#===============================================================================
class SimpleAuthentication(object):
	def __init__( self, realm, algorithm = 'MD5' ):
		super( SimpleAuthentication, self ).__init__()
		self.log = Logger().get_instance( self.__class__.__name__ )

		self.realm = realm
                self.algorithm = algorithm
                self.passwords = {}

        def getPassword( self, realm, username ):
                return self.passwords[realm + ':' + username]

	def createChallengeRequest( self, **kwargs ):
		self.log.info( str(kwargs) )

		challenge = {}
		challenge['realm'] = self.realm
		challenge['domain'] = self.realm
		challenge['nonce'] = 'xxx' #FIXME:Implement nonce generation.
		challenge['opaque'] = ''
		challenge['algorithm'] = self.algorithm
		challenge['stale'] = 'true'
		challenge['qop'] = ''
		return challenge

	def answerChallengeRequest( self, **kwargs ):
		self.log.info( str(kwargs) )

                try:
                    password = self.getPassword( kwargs['realm'], kwargs['username'] )
                except KeyError:
			raise SipException( 'Failed to find password for user, ' + kwargs['username'] + ', at realm, ' + kwargs['realm'] + '.' )
		kwargs['password'] = password

		response = {}
		response['username'] = ''
		response['realm'] = kwargs['realm']
		response['nonce'] = kwargs['nonce']
		response['uri'] = 'sip:' + response['username'] + '@' + response['realm']
		response['response'] = self.__calculateResponse( **kwargs )
		response['algorithm'] = kwargs['algorithm']
		response['cnonce'] = ''
		response['opaque'] = kwargs['opaque']
		response['qop'] = kwargs['qop']
		response['nc'] = ''
		return response

	def __calculateResponse( self, **kwargs ):
		self.log.info( str(kwargs) )

		response = ''

		if kwargs['algorithm'] == 'MD5':
			ha1 = Digest.ha1( kwargs['username'], kwargs['realm'], kwargs['password'] )
			self.log.info( 'ha1 = ' + str(ha1) )

			ha2 = Digest.ha2( kwargs['method'], str(kwargs['uri']) )
			self.log.info( 'ha2 = ' + str(ha2) )

			# FIXME: Should we use a given qop parameter or the values from our reply instead of getting them from the UA request?
			if ( kwargs.get( 'qop', '' ) == 'auth' ):
				response = Digest.response( ha1, ha2, kwargs['nonce'], kwargs['nc'], kwargs['cnonce'], kwargs['qop'] )
			else:
				response = Digest.response( ha1, ha2, kwargs['nonce'] )
		elif kwargs['algorithm'] == 'MD5-sess':
			self.log.error( 'Unsupported algorithm, ' + kwargs['algorithm'] + '.' )
		elif kwargs['algorithm'] == 'Basic':
			response = password
		else:
			self.log.error( 'Unknown algorithm, ' + kwargs['algorithm'] + '.' )

		return response

	def verifyChallengeResponse( self, **kwargs ):
		self.log.info( str(kwargs) )

		password = self.getPassword( kwargs['realm'], kwargs['username'] )
		if not password:
			raise Exception( 'Failed to find password for user, ' + kwargs['username'] + ', at realm, ' + kwargs['realm'] + '.' )
		kwargs['password'] = password

		if self.__verifyChallengeResponse( **kwargs ):
			# Success
			return None
		else:
			return self.createChallengeRequest( **kwargs )

	def __verifyChallengeResponse( self, **kwargs ):
		self.log.info( str(kwargs) )

		# Do not verify the challenge if there is no response.
		response = kwargs.get( 'response', None )
		if not response:
			return False

		expectedResponse = self.__calculateResponse( **kwargs )

		self.log.info( 'Expected a response of ' + expectedResponse + '.  Got a response of ' + response + '.' )
		if response == expectedResponse:
			return True
		else:
			self.log.warn( 'Failed to authenticate.  Expected a response of ' + expectedResponse + '.  Got a response of ' + response + '.' )
			return False
