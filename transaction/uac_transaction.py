#!/usr/bin/env python
from iron.dispatcher import Dispatcher
from iron.event import Event
from iron.state import State
from mercury.message.message import *
from mercury.transaction.transaction import *
from mercury.transaction.transaction_base import *
from threading import Timer
import logging

class UacTransaction(TransactionBase):
	"""The UacTransaction implements a non-INVITE client transaction as per RFC3261 section 17.1.2."""

	def __init__( self ):
		super( UacTransaction, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )
		self.state = State( self, self.STATE_INITIAL, { self.STATE_TRYING : self.CONFIG_TIMER_F, self.STATE_COMPLETED : self.CONFIG_TIMER_K } )
		self.timerE = None
		self.request = None
		self.lastResponse = None
		self.termination = None

	@Dispatcher.eventHandler
	def start( self, event ): pass
	@Dispatcher.eventHandler
	def cancel( self ): pass
	@Dispatcher.eventHandler
	def receive( self, event ): pass

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
		self.request = event

		self.state.changeState( self.STATE_TRYING )

		# Send request to server.
		Dispatcher.getInstance().notify( Event( self.NOTIFICATION_STARTED ), messageEvent = event ) #FIXME: This notify is also below...

		# Inform the TU.
		Dispatcher.getInstance().notify( Event( self.NOTIFICATION_STARTED ) )

	# Trying
	def inTrying_onEnter( self, event ):
		# Only start timer E if the transport is unreliable.
		if self.request.transport == 'udp':
			self.timerE = Dispatcher.getInstance().schedule( self.CONFIG_TIMER_E, Event( self.EVENT_TIMER_E ), srcObj = self, dstObj = self )

	def inTrying_onLeave( self, event ):
		self.timerE.cancel()

	def inTrying_on1xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to the TU.
		#Dispatcher.getInstance().notify( Event( self.NOTIFICATION_1xx ), messageEvent = event )

		self.state.changeState( self.STATE_PROCEEDING )

	def inTrying_on2xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to the TU.
		#Dispatcher.getInstance().notify( Event( self.NOTIFICATION_2xx ), messageEvent = event )

		self.state.changeState( self.STATE_COMPLETED )

	def inTrying_on3xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to the TU.
		#Dispatcher.getInstance().notify( Event( self.NOTIFICATION_3xx ), messageEvent = event )

		self.state.changeState( self.STATE_COMPLETED )

	def inTrying_onTimerE( self, event ):
		# Resend request to server.
		Dispatcher.getInstance().notify( self.request )

		# Restart Timer E.
		Dispatcher.getInstance().schedule( self.CONFIG_TIMER_E, Event( self.EVENT_TIMER_E ), srcObj = self, dstObj = self )

	def inTrying_onTimerF( self, event ):
		self.result = self.RESULT_TIMEOUT_F
		self.state.changeState( self.STATE_TERMINATED )

	def inTrying_onTransportError( self, event ):
		self.result = self.RESULT_TRANSPORT_ERROR
		self.state.changeState( self.STATE_TERMINATED )

	# Proceeding
	def inProceeding_on1xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to the TU.
		#Dispatcher.getInstance().notify( Event( self.NOTIFICATION_1xx ), messageEvent = event )

	def inProceeding_on2xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to the TU.
		#Dispatcher.getInstance().notify( Event( self.NOTIFICATION_2xx ), messageEvent = event )

		self.state.changeState( self.STATE_COMPLETED )

	def inProceeding_on3xx( self, event ):
		# Save response.
		self.lastResponse = event

		# Send response to the TU.
		#Dispatcher.getInstance().notify( Event( self.NOTIFICATION_3xx ), messageEvent = event )

		self.state.changeState( self.STATE_COMPLETED )

	def inProceeding_onTimerE( self, event ):
		# Resend request to server.
		Dispatcher.getInstance().notify( self.request )

		# Restart Timer E.
		Dispatcher.getInstance().schedule( self.CONFIG_TIMER_E, Event( self.EVENT_TIMER_E ), srcObj = self, dstObj = self )

	def inProceeding_onTimerF( self, event ):
		self.result = self.RESULT_TIMEOUT
		self.state.changeState( self.STATE_TERMINATED )

	def inProceeding_onTransportError( self, event ):
		self.result = self.RESULT_TRANSPORT_ERROR
		self.state.changeState( self.STATE_TERMINATED )

	# Completed
	def inCompleted_onEnter( self, event ):
		# Inform the TU.
		Dispatcher.getInstance().notify( Event( self.NOTIFICATION_COMPLETED ) )

	def inCompleted_onLeave( self, event ):
		pass

	def inCompleted_onTimerK( self, event ):
		self.result = self.RESULT_COMPLETED
		self.state.changeState( self.STATE_TERMINATED )

	# Terminated
	def inTerminated_onEnter( self, event ):
		# Inform the TU.
		Dispatcher.getInstance().notify( Event( self.NOTIFICATION_TERMINATED ), result = self.result )

