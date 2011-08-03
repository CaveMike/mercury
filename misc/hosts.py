from log4py import Logger
from event import Event
from statenode import StateNode
from host import Host
from user import User
from dialog import Dialog

#===============================================================================
class Hosts(StateNode):
	def __init__( self, name, parent = None ):
		StateNode.__init__( self, name, parent )
		self.hosts = {}

	def addHost( self, event ):
		print 'Add host ' + event[Host.KEY] + '.'
		host = Host( event[Host.KEY] )
		self.hosts[ event[Host.KEY] ] = host

	def removeHost( self, event ):
		print 'Remove host ' + event[c.KEY] + '.'
		del self.hosts[ event[Host.KEY] ]

	def onDefault( self, event ):
		if not self.hosts.has_key( event[Host.KEY] ):
			self.addHost( event )

		if self.hosts.has_key( event[Host.KEY] ):
			self.hosts[ event[Host.KEY] ].process( event )
