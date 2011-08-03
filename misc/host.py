from core import SipException
from log4py import Logger
from event import Event
from statenode import StateNode
from user import User
from dialog import Dialog
from message import *

#===============================================================================
class Host(StateNode):

	STATE_ACTIVE = 'Active'

	def __init__( self, name, parent ):
		StateNode.__init__( self, name, parent, initialState = self.STATE_ACTIVE )
		self.log = Logger().get_instance( self.__class__.__name__ )

		self.users = {}

	def identifyEvent( self, event ):
		self.log.info( str(event) )
		if isinstance( event, MessageEvent ):
			return event.id
		elif isinstance( event, StateChangeNotification ):
			if event.node in self.users.itervalues():
				return 'User' + event.node.currentState

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	def inActive_onRxRequest( self, event ):
		userName = event.message['To'].uri.user
		if not userName in self.users:
			user = User( userName, self )
			user.addListener( self )
			self.users[userName] = user

		event.localUser = self.users[userName]
		self.send( event, event.localUser, False )

	def inActive_onRxResponse( self, event ):
		userName = event.message['From'].uri.user
		if not userName in self.users:
			self.users[userName] = User( userName, self )

		event.localUser = self.users[userName]
		self.send( event, event.localUser, False )

	def inActive_onTxRequest( self, event ):
		self.notify( event, False )

	def inActive_onTxResponse( self, event ):
		self.notify( event, False )
