#!/usr/bin/env python
from iron.state import State
from mercury.transaction.transaction import Transaction
from mercury.transaction.transaction_base import TransactionBase
from mercury.message.message import Request
from mercury.message.message import MessageEvent
from mercury.core import SipException
import logging

#===============================================================================
class UasTransactionInvite(TransactionBase):
	"""The UasTransactionInvite class does something."""

	STATE_INITIAL    = 'Initial'
	STATE_PROCEEDING = 'Proceeding'
	STATE_COMPLETED  = 'Completed'
	STATE_CONFIRMED  = 'Confirmed'
	STATE_TERMINATED = 'Terminated'

	EVENT_INVITE          = 'INVITE'
	EVENT_1xx             = '1xx'
	EVENT_2xx             = '2xx'
	EVENT_3xx             = '3xx'
	EVENT_ACK             = 'ACK'
	EVENT_TRANSPORT_ERROR = 'TransportError'
	EVENT_TIMER_G         = 'TimerG'
	EVENT_TIMER_H         = 'TimerH'
	EVENT_TIMER_I         = 'TimerI'

	def __init__( self, auto100 = True ):
		super( UasTransactionInvite, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )
		self.state = State( self, self.STATE_INITIAL, {} )
		self.auto100 = auto100

	def identifyEvent( self, event ):
		if isinstance(event, MessageEvent):
			if isinstance(event.message, Request):
				if event.message.method in [ 'ACK', 'BYE', 'CANCEL', 'INVITE', 'PRACK' ]:
					return event.message.method
			elif event.message.statusClass == 1:
				return self.EVENT_1xx
			elif event.message.statusClass == 2:
				return self.EVENT_2xx
			elif event.message.statusClass >= 3:
				return self.EVENT_3xx

		raise SipException( 'Ignoring event ' + str(event) + '.' )

	# Initial
	def inInitial_onINVITE( self, event ):
		# Pass request to TU.
		if self.auto100:
			# Send 100 response to client.
			pass
		self.changeState( UasTransactionInvite.STATE_PROCEEDING )

	# Proceeding
	def inProceeding_onINVITE( self, event ):
		# Resend response to client.
		pass

	def inCalling_on1xx( self, event ):
		# Save response.
		# Send response to client.
		pass

	def inCalling_on2xx( self, event ):
		# Save response.
		# Send response to client.
		self.changeState( UasTransactionInvite.STATE_TERMINATED )

	def inCalling_on3xx( self, event ):
		# Save response.
		# Send response to client.
		self.changeState( UasTransactionInvite.STATE_COMPLETED )

	def inCalling_onTransportError( self, event ):
		# Inform the TU.
		self.changeState( UasTransactionInvite.STATE_TERMINATED )

	# Completed
	def inProceeding_onINVITE( self, event ):
		# Resend response to client.
		pass

	def inCompleted_onTimerG( self, event ):
		# Resend response to client.
		# Restart Timer G?
		pass

	def inCompleted_onACK( self, event ):
		self.changeState( UasTransactionInvite.STATE_CONFIRMED )

	def inCompleted_onTimerH( self, event ):
		# Inform the TU.
		self.changeState( UasTransactionInvite.STATE_TERMINATED )

	def inCompleted_onTransportError( self, event ):
		# Inform the TU.
		self.changeState( UasTransactionInvite.STATE_TERMINATED )

	# Confirmed
	def inConfirmed_onTimerI( self, event ):
		self.changeState( UasTransactionInvite.STATE_TERMINATED )

	# Terminated
