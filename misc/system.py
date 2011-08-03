from core import SipException
from configuration import ConfigEvent
from configuration import Configuration
from event import Event
from log4py import Logger
from message import MessageEvent
from network import NetEvent
from message_adapter import MessageAdapter
from statenode import StateChangeNotification
from statenode import StateNode
from resources import Resources
from resources import ResourceEvent

#===============================================================================
class System(StateNode):

	STATE_STOPPED = 'Stopped'
	STATE_STARTED = 'Started'
	STATE_PAUSED  = 'Paused'

	EVENT_START    = 'Start'
	EVENT_PAUSE    = 'Pause'
	EVENT_CONTINUE = 'Continue'
	EVENT_STOP     = 'Stop'

	def __init__( self, name, parent ):
		StateNode.__init__( self, name, parent, initialState = System.STATE_STOPPED )
		self.log = Logger().get_instance( self.__class__.__name__ )

		self.config = Configuration( 'config', self )
		self.config.addListener( self )

		self.network = MessageAdapter( 'msg_net', self )
		self.network.addListener( self )

		self.resources = Resources( 'resources', self )
		self.resources.addListener( self )

		self.addListener( parent )

	def identifyEvent( self, event ):
		self.log.info( str(event) )

		if isinstance( event, MessageEvent ):
			return event.id
		elif isinstance( event, ConfigEvent ):
			return event.id
		elif isinstance( event, StateChangeNotification ):
			return event.id
		else:
			# Local events.
			return event.id

	# Stopped
	def inStopped_onStart( self, event ):
		self.send( Event( Configuration.EVENT_READ ), self.config, queued=False )

		self.send( ResourceEvent( ResourceEvent.EVENT_BIND, uri='sip.example.com', clsName='user-agent' ), self.resources, queued=False )
		self.send( NetEvent( NetEvent.EVENT_BIND, transport=self.query( 'network.transport' ), localAddress=self.query( 'network.localAddress' ), localPort=self.query( 'network.localPort' ) ), self.network, queued=False )

		self.changeState( self.STATE_STARTED )
		event.handled = True

	# Started
	def inStarted_onStop( self, event ):
		self.changeState( self.STATE_STOPPED )
		event.handled = True

	def inStarted_onPause( self, event ):
		self.changeState( self.STATE_PAUSED )
		event.handled = True

	def inStarted_onRxRequest( self, event ):
		self.send( event, self.resources, queued=False )

	def inStarted_onRxResponse( self, event ):
		self.send( event, self.resources, queued=False )

	def inStarted_onTxRequest( self, event ):
		self.send( event, self.network, queued=False )

	def inStarted_onTxResponse( self, event ):
		self.send( event, self.network, queued=False )

	# Paused
	def inPaused_onContinue( self, event ):
		self.changeState( self.STATE_STARTED )
		event.handled = True

	def query( self, name, active = True, args = None, kwargs = None ):
		return self.config.query( name, active, args, kwargs )
