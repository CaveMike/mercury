from log4py import Logger
from event import Event
from statenode import StateNode
from host import Host
from user import User
from dialog import Dialog
import unittest

#===============================================================================
class TestHost(unittest.TestCase):
	def runTest( self ):

		root = Host( 'host0' )

		root.process( Event( 'AddUser', { Host.KEY:'12.1.1.1', User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( 'AddDialog', { Host.KEY:'12.1.1.1', User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( '1xx', { Host.KEY:'12.1.1.1',  User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( '200', { Host.KEY:'12.1.1.1',  User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( 'BYE', { Host.KEY:'12.1.1.1',  User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( 'Dump', { Host.KEY:'12.1.1.1',  User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( 'RemoveDialog', { Host.KEY:'12.1.1.1', User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print
		root.process( Event( 'RemoveUser', { Host.KEY:'12.1.1.1', User.KEY:'riley', Dialog.KEY:'c2' } ) )
		print

		assert 1

if __name__ == "__main__":
	unittest.main()
