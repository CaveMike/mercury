from authentication_adapter import AuthenticationAdapter
from configuration import ConfigEvent
from core import SipException
from dialog import Dialog
from dialog import DialogEvent
from event import Event
from host import Host
from log4py import Logger
from message import *
from statenode import StateChangeNotification
from statenode import StateNode
from transaction import Transaction
from transaction import TransactionEvent

#===============================================================================
class UserAgent(StateNode):

	STATE_ACTIVE = 'Active'

	def __init__( self, name, parent ):
		StateNode.__init__( self, name, parent, initialState = self.STATE_ACTIVE )
		self.log = Logger().get_instance( self.__class__.__name__ )

		self.authentication = AuthenticationAdapter( 'auth_adapter', self )
		self.authentication.addListener( self )
		self.authentication = None #FIXME:

		self.transactions = {}
		self.dialogs = {}

	def identifyEvent( self, event ):
		self.log.info( str(event) )

		if isinstance( event, MessageEvent ):
			event.useragent = self
			return event.id
		elif isinstance( event, StateChangeNotification ):
			return event.id

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	def getTransaction( self, event, createIfMissing ):
		#FIXME: transaction key is more complex than call-id.
		key = event.message['Call-ID']

		try:
			transaction = self.transactions[key]
		except KeyError:
			if createIfMissing:
				# No transaction available, create a new one.
				transaction = Transaction( key, self, event )
				if transaction:
					transaction.addListener( self )
					self.transactions[key] = transaction
			else:
				transaction = None

		return transaction

	def getDialog( self, event, createIfMissing ):
		#FIXME: dialog key is more complex than call-id.
		key = event.message['Call-ID']

		try:
			dialog = self.dialogs[key]
		except KeyError:
			if createIfMissing:
				# No dialog available, create a new one.
				dialog = Dialog( key, self, event )
				if dialog:
					dialog.addListener( self )
					self.dialogs[key] = dialog
			else:
				dialog = None

		return dialog

	def _inActive_onRx( self, event ):
		transaction = self.getTransaction( event, createIfMissing=True )
		if transaction:
			self.send( event, transaction, queued=False )

		dialog = self.getDialog( event, createIfMissing=True )
		if dialog:
			self.send( event, dialog, queued=False )

		event.handled = True

	def inActive_onRxRequest( self, event ):
		if self.authentication:
			# Authenticate incoming requests.
			# If the request fails authentication, a 401/407 will be sent automatically
			# and event.handled will be true.
			self.send( event, self.authentication, queued=False )

		if not event.handled:
			# Request authenticated successfully.
			self._inActive_onRx( event )

	def inActive_onRxResponse( self, event ):
		if self.authentication:
			# Check the authentication status of incoming responses.
			# If the response indicates that the request failed to authentication,
			# then the request will be re-sent with authentication automatically
			# and event.handled will be true.
			self.send( event, self.authentication, queued=False )

		if not event.handled:
			# Request authenticated successfully.
			self._inActive_onRx( event )

	def inActive_onTxRequest( self, event ):
		if not event.message['UserAgent'].type:
			event.message['UserAgent'] = self.query( 'sip.useragent' )

		self.send( event, self.parent, False )

		event.handled = True

	def inActive_onTxResponse( self, event ):
		if not event.message['Server'] or not event.message['Server'].type:
			event.message['Server'] = self.query( 'sip.useragent' )

		self.send( event, self.parent, False )

		event.handled = True
