from core import SipException
from event import Event
from helpers import importExtension
from log4py import Logger
from message import Message
from message import MessageEvent
from node import Node

#===============================================================================
class ResourceEvent(Event):
	EVENT_BIND      = 'Bind'
	EVENT_UNBIND    = 'Unbind'

	def __init__( self, id, uri, clsName ):
		super( ResourceEvent, self ).__init__( id )
		self.uri = uri
		self.clsName = clsName

	def __str__( self ):
		return '%s, uri: %s, clsName: %s' % ( Event.__str__(self), str(self.uri), str(self.clsName) )

#===============================================================================
class Resources(Node):
	"""Dispatches incoming MessageEvents based on the Request-URI."""

	def __init__( self, name, parent ):
		super( Resources, self ).__init__( name, parent )
		self.log = Logger().get_instance( self.__class__.__name__ )

		self.resources = {}

	def identifyEvent( self, event ):
		self.log.info( str(event) )

		if isinstance( event, MessageEvent ):
			return event.id
		elif isinstance( event, ResourceEvent ):
			return event.id

		raise SipException( '[' + str(self.name) + '] ' + 'Ignoring event ' + str(event) + '.' )

	def onBind( self, event ):
		obj = importExtension( event.clsName )
		if obj:
			resource = obj( str(event.uri), self )
			if resource:
				resource.addListener( self )
				self.resources[event.uri] = resource

		if not obj or not resource:
			raise Exception( 'Failed to import resource, ' + str(event.uri) + ', of type, ' + str(event.clsName) + '.' )

		event.handled = True

	def onUnbind( self, event ):
		del self.resources[event.uri]

		event.handled = True


	def onRxRequest( self, event ):
		try:
			host = event.message.requestUri.host

			resource = self.resources[host]

			self.send( event, resource, queued=False )
		except KeyError:
			pass

	def onRxResponse( self, event ):
		raise 'FIXME:IMPLEMENT: Need to find the corresponding request, then the request-URI, then look up the resource in self.resources.'

	def onTxRequest( self, event ):
		self.notify( event, queued=False )

	def onTxResponse( self, event ):
		self.notify( event, queued=False )
