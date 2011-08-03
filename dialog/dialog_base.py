#!/usr/bin/env python
from mercury.transaction.transaction_base import TransactionBase

#===============================================================================
class DialogBase(object):

	EVENT_1xx     = '1xx'
	EVENT_2xx     = '2xx'
	EVENT_3xx     = '3xx'

	STATE_INITIAL     = 'Initial'
	STATE_PROCEEDING  = 'Proceeding'
	STATE_EARLY       = 'Early'
	STATE_CONFIRMED   = 'Confirmed'
	STATE_UPDATING    = 'Updating'
	STATE_NEGOTIATING = 'Negotiating'
	STATE_TERMINATED  = 'Terminated'

	NOTIFICATION_REQUEST   = 'Request'
	NOTIFICATION_1xx       = '1xx'
	NOTIFICATION_2xx       = '2xx'
	NOTIFICATION_3xx       = '3xx'
	NOTIFICATION_STARTED   = 'Started'
	NOTIFICATION_COMPLETED = 'Completed'
	NOTIFICATION_TRYING     = TransactionBase.STATE_TRYING
	NOTIFICATION_PROCEEDING = TransactionBase.STATE_PROCEEDING
	NOTIFICATION_COMPLETED  = TransactionBase.STATE_COMPLETED
	NOTIFICATION_TERMINATED = TransactionBase.STATE_TERMINATED
