#! /usr/bin/python
from network import BindingBase
import logging

class SctpBinding(BindingBase):
	def __init__( self, name, parent, event ):
		super( SctpBinding, self ).__init__( name, parent, initialState = self.STATE_INITIAL )
		self.log =  logging.getLogger( self.__class__.__name__ )
