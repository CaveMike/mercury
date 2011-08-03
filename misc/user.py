from core import SipException
from log4py import Logger
from event import Event
from statenode import *
from dialog import *
from message import *

#===============================================================================
class User(StateNode):
	STATE_ACTIVE = 'Active'

	def __init__( self, name, parent ):
		StateNode.__init__( self, name, parent, initialState = self.STATE_ACTIVE )
		self.log = Logger().get_instance( self.__class__.__name__ )
		self.dialogs = {}

	def identifyEvent( self, event ):
		self.log.info( str(event) )
		if isinstance( event, MessageEvent ):
			return event.id
		elif isinstance( event, StateChangeNotification ):
			if event.node in self.dialogs.itervalues():
				return 'Dialog' + event.node.currentState

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	def inActive_onRxRequest( self, event ):
		callid = event.message['Call-ID']
		if not callid in self.dialogs:
			dialog = Dialog( callid, self, event )
			dialog.addListener( self )
			self.dialogs[callid] = dialog

#FIXME: We don't really want to create a dialog for everything (e.g. REGISTER).
#       Even if we create a dummy dialog, then the subscribe and register dialogs would conflict.
		dialog = self.dialogs[callid]
		self.send( event, dialog, False )

	def inActive_onRxResponse( self, event ):
		callid = event.message['Call-ID']
		if not callid in self.dialogs:
			self.handled = True
			raise SipException( 'Dialog, ' + str(callid) + ' not found in user, ' + str(self.name) + '.' )
		else:
			dialog = self.dialogs[callid]
			self.send( event, dialog, False )

	def inActive_onTxRequest( self, event ):
		self.notify( event, False )

	def inActive_onTxResponse( self, event ):
		self.notify( event, False )

	def inActive_onDialogEarly( self, event ):
		#FIXME:
		self.inActive_onDialogProceeding( self, event )

	def inActive_onDialogProceeding( self, event ):
		dialog = [ d for d in self.dialogs.itervalues() ][0]
		transaction = dialog.transaction
		#FIXME:
		e = transaction.lastRequestEvent
		ne = createResponseEvent( e, 200 )
		self.notify( ne, True )
		event.handled = True
