from log4py import Logger
from event import Event
from statenode import StateNode

#===============================================================================
class Peers(StateNode):
	def __init__( self, name, parent = None ):
		StateNode.__init__( self, name, parent )
