from event import Event
from statenode import *
from log4py import Logger
from dialog import *
from message import *
from transaction import *
from threading import Timer

#===============================================================================
class SubscriptionEvent(Event):

	def __init__( self, id, user = None, subscriptionSource = None, resourceUri = None, event = None, contentType = None, expires = None, silent = False ):
		Event.__init__( self, id )
		self.user = user
		self.subscriptionSource = subscriptionSource
		self.resourceUri = resourceUri
		self.event = event
		self.contentType = contentType
		self.expires = expires
		self.silent = silent

	def __str__( self ):
		return '%s, user: %s, source = %s, resource: %s, event: %s, type: %s, expires: %s, silent: %s' % ( Event.__str__(self), str(self.user.name), str(self.subscriptionSource), str(self.name), str(self.resourceUri), str(self.event), str(self.contentType), str(self.expires), str(self.silent) )

#===============================================================================
#class SubscriptionNotification(Event):
#
#	def __init__( self, id, subscription ):
#		Event.__init__( self, id )
#		self.subscription = subscription
#
#	def __str__( self ):
#		return '%s, subscription: %s' % ( Event.__str__(self), str(self.name) )

#===============================================================================
class UacSubscription(StateNode):
	EVENT_SUBSCRIBE   = 'Subscribe'
	EVENT_RESUBSCRIBE = 'Resubscribe'
	EVENT_UNSUBSCRIBE = 'Unsubscribe'
	EVENT_TERMINATE   = 'Terminate'

	STATE_INITIAL       = 'Initial'
	STATE_SUBSCRIBING   = 'Subscribing'
	STATE_SUBSCRIBED    = 'Subscribed'
	STATE_UNSUBSCRIBING = 'Unsubscribing'
	STATE_UNSUBSCRIBED  = 'Unsubscribed'

	#
	# App Events
	# 	subscribe
	# 	resubscribe
	# 	unsubscribe( silently )
	#
	# Dialog events
	#	transaction error/timeout
	#	net error
	#	proceeding
	#	confirmed
	#	terminated
	#
	# Internal events
	# 	resubscribe timeout
	#	retry timeout
	#
	# Listener notifications
	#	state changed
	#	received notify

	def __init__( self, name, parent, subscriptionSource, user, resourceUri, event, contentType, expires ):
		StateNode.__init__( self, name, parent, initialState = self.STATE_INITIAL )
		self.user = user
		self.subscriptionSource = subscriptionSource
		self.resourceUri = resourceUri
		self.event = event
		self.contentType = contentType
		self.reqExpires = expires
		self.rspExpires = None
		self.dialog = None
		self.resubscribeTimer = None
		self.retryTimter = None
		self.addListener( parent )

	def __iter__( self ):
		return self.dialog

	def identifyEvent( self, event ):
		if isinstance( event, MessageEvent ):
			if isinstance( event.message, Request ):
				if event.message.method == 'NOTIFY':
					event.id = event.message.method
		elif isinstance( event, StateChangeNotification ):
			if event.node == self.dialog:
				event.id = event.node.currentState

#		raise Exception( 'Unknown event, ' + str(event) + '.' )
		return event.id

	# Initial
	def inInitial_onSubscribe( self, event ):
		self.dialog = UacDialogSubscribe( 'dialog0', self )
		self.dialog.addListener( self )
		request = Request()
#		request.To =
#		request.From =
#		request.Contact =
		request.CallID = self.dialog.name
		request.Expires = self.reqExpires
		self.send( MessageEvent( message=request ), self.dialog, False )
		event.handled = True

	def inInitial_onProceeding( self, event ):
		self.changeState( self.STATE_SUBSCRIBING )
		event.handled = True

	# Subscribing
	def inSubscribing_onConfirmed( self, event ):
		self.changeState( self.STATE_SUBSCRIBED )
		event.handled = True

	# Subscribed
	def inSubscribed_onUnsubscribe( self, event ):
		request = Request()
#		request.To =
#		request.From =
#		request.Contact =
		request.CallID = self.dialog.name
		request.Expires = 0
		self.send( MessageEvent( message=request ), self.dialog, False )
		self.changeState( self.STATE_UNSUBSCRIBING )
		event.handled = True

	def inSubscribed_onTerminate( self, event ):
		self.changeState( self.STATE_UNSUBSCRIBED )
		event.handled = True

	def inSubscribed_onTerminated( self, event ):
		self.changeState( self.STATE_UNSUBSCRIBED )
		event.handled = True

	# Unsubscribing
	def inUnsubscribing_onTerminated( self, event ):
		self.changeState( self.STATE_UNSUBSCRIBED )
		event.handled = True

	# Unsubscribed
	def inUnsubscribing_onRetry( self, event ):
		self.changeState( self.STATE_SUBSCRIBING )
		event.handled = True

	def onRx( self, event ):
		self.send( event, self.dialog, False )
