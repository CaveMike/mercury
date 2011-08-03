#!/usr/bin/env python
from iron.state import State
from mercury.transaction.transaction import *
from mercury.transaction.transaction_base import *
import logging

#===============================================================================
class UacTransactionInvite(TransactionBase):
	"""The UacTransactionInvite class does something."""

	STATE_INITIAL    = 'Initial'
	STATE_CALLING    = 'Calling'
	STATE_PROCEEDING = 'Proceeding'
	STATE_COMPLETED  = 'Completed'
	STATE_TERMINATED = 'Terminated'

	EVENT_INVITE          = 'INVITE'
	EVENT_1xx             = '1xx'
	EVENT_2xx             = '2xx'
	EVENT_3xx             = '3xx'
	EVENT_ACK             = 'ACK'
	EVENT_TRANSPORT_ERROR = 'TransportError'
	EVENT_TIMER_A         = 'TimerA'
	EVENT_TIMER_B         = 'TimerB'
	EVENT_TIMER_D         = 'TimerD'

	def __init__( self, autoAckOn2xx = False ):
		super( UacTransactionInvite, self ).__init__()
		self.log = logging.getLogger( self.__class__.__name__ )
		self.state = State( self, self.STATE_INITIAL, {} )
		self.autoAckOn2xx = autoAckOn2xx

	# Initial
	def inInitial_onINVITE( self, event ):
		# Send INVITE to server.
		self.changeState( UacTransactionInvite.STATE_PROCEEDING )

	# Trying
	def inCalling_on1xx( self, event ):
		# Save response.
		# Send response to the TU.
		self.changeState( UacTransactionInvite.STATE_PROCEEDING )

	def inCalling_on2xx( self, event ):
		# Save response.
		# Send response to the TU.
		if self.autoAckOn2xx:
			# Send ACK to server.
			pass
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	def inCalling_on3xx( self, event ):
		# Save response.
		# Send response to the TU.
		# Send ACK to server.
		self.changeState( UacTransactionInvite.STATE_COMPLETED )

	def inCalling_onTimerA( self, event ):
		# Resend the request to server.
		pass

	def inCalling_onTimerB( self, event ):
		# Inform the TU.
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	def inCalling_onTransportError( self, event ):
		# Inform the TU.
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	# Proceeding
	def inProceeding_on1xx( self, event ):
		# Save response.
		# Send response to the TU.
		pass

	def inProceeding_on2xx( self, event ):
		# Save response.
		# Send response to the TU.
		if self.autoAckOn2xx:
			# Send ACK to server.
			pass
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	def inProceeding_on3xx( self, event ):
		# Save response.
		# Send response to the TU.
		# Send ACK to server.
		self.changeState( UacTransactionInvite.STATE_COMPLETED )

	def inProceeding_onTransportError( self, event ):
		# Inform the TU.
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	# Completed
	def inProceeding_on3xx( self, event ):
		# Save response.
		# Send response to the TU.
		# Send ACK to server.
		pass

	def inCompleted_onTimerD( self, event ):
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	def inProceeding_onTransportError( self, event ):
		# Inform the TU.
		self.changeState( UacTransactionInvite.STATE_TERMINATED )

	# Terminated
