#!/usr/bin/env python
from iron.dispatcher import Dispatcher
from iron.event import Event
from iron.state import State
from mercury.transaction.transaction_base import *
from mercury.message.message import *
from mercury.transaction.transaction import TransactionEvent
import logging

class UasTransaction(TransactionBase):
	"""The UacTransaction implements a non-INVITE server transaction as per RFC3261 section 17."""


	def __init__( self, auto100 = True ):
		super( UasTransaction, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )
		self.state = State( self, self.STATE_INITIAL, { self.STATE_COMPLETED : self.CONFIG_TIMER_J } )
		self.auto100 = auto100
		self.lastRequest = None
		self.lastResponse = None
		self.result = None

	def identifyEvent( self, event ):
		if isinstance(event, MessageEvent):
			if isinstance(event.message, Request):
				return self.EVENT_REQUEST
			elif event.message.statusClass == 1:
				return self.EVENT_1xx
			elif event.message.statusClass == 2:
				return self.EVENT_2xx
			elif event.message.statusClass >= 3:
				return self.EVENT_3xx
		else:
			return event()

		raise SipException( 'Ignoring event ' + str(event) + '.' )

	def identifyState( self, event ):
		return self.state.identifyState( event )

	# Initial
	def inInitial_onRequest( self, event ):
		self.lastRequest = event

		# Pass request to TU.
		if self.auto100:
			# Send 100 response to client.
			e = createResponseEvent( event, 100 )
			Dispatcher.getInstance().notify( e )

		self.state.changeState( self.STATE_TRYING )

	# Trying
	def inTrying_on1xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to client.
		self.state.changeState( self.STATE_PROCEEDING )

	def inTrying_on2xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to client.
		self.state.changeState( self.STATE_COMPLETED )

	def inTrying_on3xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to client.
		self.state.changeState( self.STATE_COMPLETED )

	# Proceeding
	def inProceeding_onRequest( self, event ):
		# Resend response to client.
		Dispatcher.getInstance().notify( self.lastResponse )

	def inProceeding_on1xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to client.
#		Dispatcher.getInstance().notify( event )

	def inProceeding_on2xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Inform the TU.
		self.state.changeState( self.STATE_COMPLETED )

	def inProceeding_on3xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to client.
		self.state.changeState( self.STATE_COMPLETED )

	def inProceeding_onTransportError( self, event ):
		self.result = self.RESULT_TRANSPORT_ERROR
		self.state.changeState( self.STATE_TERMINATED )

	# Completed
	def inCompleted_onEnter( self, event ):
		# Inform the TU.
		Dispatcher.getInstance().notify( Event( self.NOTIFICATION_COMPLETED ) )

	def inCompleted_onRequest( self, event ):
		# Resend response to client.
		Dispatcher.getInstance().notify( self.lastResponse )

	def inCompleted_onTransportError( self, event ):
		self.result = self.RESULT_TRANSPORT_ERROR
		self.state.changeState( self.STATE_TERMINATED )

	def inCompleted_onTimerJ( self, event ):
		self.result = self.RESULT_TIMEOUT_J
		self.state.changeState( self.STATE_TERMINATED )

	# Terminated
	def inTerminated_onEnter( self, event ):
		# Inform the TU.
		Dispatcher.getInstance().notify( Event( self.NOTIFICATION_TERMINATED ), result = self.result )

