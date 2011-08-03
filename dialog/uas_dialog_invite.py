#!/usr/bin/env python
from iron.event import Event
from iron.state import State
from mercury.core import SipException
from mercury.dialog.dialog_base import *
from mercury.message.message import *
from mercury.transaction.transaction import *
from mercury.transaction.uas_transaction import UasTransaction
from threading import Timer
import logging

#===============================================================================
class UasDialogInvite(DialogBase):

	def __init__( self, name, parent, event ):
		super( UasDialogInvite, self ).__init__()
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

#	def __iter__( self ):
#		return self.transaction

	def identifyEvent( self, event ):
		if isinstance( event, MessageEvent ):
			if isinstance( event.message, Request ):
				if event.message.method in [ 'ACK', 'BYE', 'CANCEL', 'INVITE', 'PRACK' ]:
					print str(event.message.method)
					return str(event.message.method)
			elif event.message.statusClass == 1:
				return self.EVENT_1xx
			elif event.message.statusClass == 2:
				return self.EVENT_2xx
			elif event.message.statusClass >= 3:
				return self.EVENT_3xx
		elif isinstance( event, StateChangeNotification ):
			if event.node is self.transaction:
				return event.node.currentState

		raise SipException( 'Unknown event, ' + str(event) + '.' )

	# Initial
	def inInitial_onINVITE( self, event ):
		# Send request to server.
#		self.transaction = UasTransaction( event.message['Call-ID'], self, event )
#		self.transaction.addListener( self )
#		self.send( event, self.transaction, False )
		pass

	def inInitial_onTrying( self, event ):
		self.changeState( self.STATE_PROCEEDING, notify = True )

	def inInitial_onProceeding( self, event ):
		# Send request to server.
		self.changeState( self.STATE_PROCEEDING, notify = True )

	# Proceeding
#	def inProceeding_onResponse( self, event ):
#		if event.message.statusClass == 1:
#			self.changeState( self.STATE_EARLY, notify = True )
#		elif event.message.statusClass == 2:
#			self.changeState( self.STATE_CONFIRMED, notify = True )
#		elif event.message.statusClass >= 3:
#			self.changeState( self.STATE_TERMINATED, notify = True )

	def inProceeding_on1xx( self, event ):
		self.changeState( self.STATE_EARLY, notify = True )

	def inProceeding_on2xx( self, event ):
		self.changeState( self.STATE_CONFIRMED, notify = True )

	def inProceeding_on3xx( self, event ):
		self.changeState( self.STATE_TERMINATED, notify = True )

	# Early
	def inEarly_on1xx( self, event ):
		pass

	def inEarly_on2xx( self, event ):
		self.changeState( self.STATE_CONFIRMED, notify = True )

	def inEarly_on3xx( self, event ):
		self.changeState( self.STATE_TERMINATED, notify = True )

	# Confirmed
#	def inConfirmed_on1xx( self, event ):
#		self.changeState( self.STATE_EARLY )

	def inConfirmed_on2xx( self, event ):
		self.changeState( self.STATE_CONFIRMED, notify = True )

	def inConfirmed_onBYE( self, event ):
		self.changeState( self.STATE_TERMINATED, notify = True )

	def inConfirmed_onDefault( self, event ):
		print 'Default ' + event.id

	# Updating

	# Negotiating

	# Terminated
	def inTerminated_onDefault( self, event ):
		pass
