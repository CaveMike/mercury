#!/usr/bin/env python
from iron.event import Event
from iron.state import State
from iron.dispatcher import Dispatcher
from mercury.message.message import *
from mercury.transaction.transaction import *
from mercury.transaction.transaction_base import *
from threading import Timer
from mercury.dialog.dialog_base import *
import logging

#===============================================================================
class UasDialogSubscribe(DialogBase):

	EVENT_1xx     = '1xx'
	EVENT_2xx     = '2xx'
	EVENT_3xx     = '3xx'

	STATE_INITIAL     = 'Initial'
	STATE_PROCEEDING  = 'Proceeding'
	STATE_EARLY       = 'Early'
	STATE_CONFIRMED   = 'Confirmed'
	STATE_UPDATING    = 'Updating'
	STATE_NEGOTIATING = 'Negotiating'
	STATE_TERMINATED  = 'Terminated'

	NOTIFICATION_REQUEST   = 'Request'
	NOTIFICATION_1xx       = '1xx'
	NOTIFICATION_2xx       = '2xx'
	NOTIFICATION_3xx       = '3xx'
	NOTIFICATION_STARTED   = 'Started'
	NOTIFICATION_COMPLETED = 'Completed'
	NOTIFICATION_TRYING     = TransactionBase.STATE_TRYING
	NOTIFICATION_PROCEEDING = TransactionBase.STATE_PROCEEDING
	NOTIFICATION_COMPLETED  = TransactionBase.STATE_COMPLETED
	NOTIFICATION_TERMINATED = TransactionBase.STATE_TERMINATED

	def __init__( self ):
		super( UasDialogSubscribe, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )
		self.state = State( self, self.STATE_INITIAL, {} )
		self.callid = None
		self.localUri = None
		self.localCSeq = None
		self.localContact = None
		self.remoteUri = None
		self.remoteCSeq = None
		self.remoteContact = None
		self.transaction = None
		self.transactions = []

	def __iter__( self ):
		return self.transaction

	def identifyEvent( self, event ):
		if isinstance( event, MessageEvent ):
			if isinstance( event.message, Request ):
				return event.message.method
			elif isinstance( event.message, Response ):
				return event.id
		elif isinstance( event, StateChangeNotification ):
			if event.node is self.transaction:
				return 'Transaction' + event.node.currentState

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	# Initial
	def inInitial_onSUBSCRIBE( self, event ):
		self.transaction = Transaction( event.message['Call-ID'], self, event )
		# Send request to server.
		Dispatcher.getInstance().send( event, srcObj = self, dstObj = self.transaction )

	def inInitial_onTransactionTrying( self, event ):
		self.changeState( self.STATE_PROCEEDING, notify = True )

	def inProceeding_onTransactionCompleted( self, event ):
		if event.event.message['Expires']:
			self.changeState( self.STATE_CONFIRMED, notify = True )
		else:
			self.changeState( self.STATE_TERMINATED, notify = True )

	# Confirmed
	def inConfirmed_onSUBSCRIBE( self, event ):
		self.transaction = Transaction( event.message['Call-ID'], self, event )
		# Send request to server.
		Dispatcher.getInstance().send( event, srcObj = self, dstObj = self.transaction )

	def inConfirmed_onTransactionCompleted( self, event ):
		if event.event.message['Expires']:
			self.changeState( self.STATE_CONFIRMED, notify = True )
		else:
			self.changeState( self.STATE_TERMINATED, notify = True )

	# Terminated

	# Default
	def onRxRequest( self, event ):
		Dispatcher.getInstance().send( event, srcObj = self, dstObj = self.transaction )

	def onRxResponse( self, event ):
		Dispatcher.getInstance().send( event, srcObj = self, dstObj = self.transaction )

	def onTxRequest( self, event ):
		Dispatcher.getInstance().notify( event )

	def onTxResponse( self, event ):
		Dispatcher.getInstance().notify( event )
