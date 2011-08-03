#!/usr/bin/env python
from mercury.core import SipException
from carbon.importer import importExtension
from iron.state import StateEvent
import logging

class DialogEvent(StateEvent): pass

class Dialog(type):
	def __new__( cls, name, parent, event ):
		if event.id == 'RxRequest':
			prefix = 'uas_dialog'
		elif event.id == 'RxResponse':
			prefix = 'uac_dialog'
		elif event.id == 'TxRequest':
			prefix = 'uac_dialog'
		elif event.id == 'TxResponse':
			prefix = 'uas_dialog'

		obj = importExtension( prefix + '_' + event.message.method )
		if not obj:
			obj = importExtension( prefix )

		if obj:
			return obj( prefix + '-' + str(name), parent, event )

		raise SipException( 'Cannot create ' + prefix + ' for ' + str(event) + '.' )
