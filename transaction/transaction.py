#!/usr/bin/env python
from carbon.importer import importExtension
from iron.state import StateEvent
import logging

class TransactionEvent(StateEvent): pass

class Transaction(type):
	def __new__( cls, name, parent, event ):
		if event.id == 'RxRequest':
			prefix = 'uas_transaction'
		elif event.id == 'RxResponse':
			prefix = 'uac_transaction'
		elif event.id == 'TxRequest':
			prefix = 'uac_transaction'
		elif event.id == 'TxResponse':
			prefix = 'uas_transaction'

		obj = importExtension( prefix + '_' + event.message.method )
		if not obj:
			obj = importExtension( prefix )

		if obj:
			return obj( prefix + '-' + str(name), parent, event )

		raise SipException( 'Cannot create ' + prefix + ' for ' + str(event) + '.' )

