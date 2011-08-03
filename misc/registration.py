#===============================================================================
class Registration(object):
	def __init__( self, contact ):
		self.log = Logger().get_instance( self.__class__.__name__ )

		self.contact = contact
		self.aor = aor
		self.expires = 0

