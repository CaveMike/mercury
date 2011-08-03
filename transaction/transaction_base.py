#!/usr/bin/env python
from iron.state import StateEvent
import logging

class TransactionBase(object):
	EVENT_REQUEST = 'Request'
	EVENT_1xx     = '1xx'
	EVENT_2xx     = '2xx'
	EVENT_3xx     = '3xx'
	EVENT_TIMER_A = 'TimerA'
	EVENT_TIMER_B = 'TimerB'
	EVENT_TIMER_D = 'TimerD'
	EVENT_TIMER_E = 'TimerE'
	EVENT_TIMER_F = 'TimerF'
	EVENT_TIMER_G = 'TimerG'
	EVENT_TIMER_H = 'TimerH'
	EVENT_TIMER_I = 'TimerI'
	EVENT_TIMER_J = 'TimerJ'
	EVENT_TIMER_K = 'TimerK'

	STATE_INITIAL    = 'Initial'
	STATE_TRYING     = 'Trying'
	STATE_PROCEEDING = 'Proceeding'
	STATE_COMPLETED  = 'Completed'
	STATE_TERMINATED = 'Terminated'

	#NOTIFICATION_REQUEST    = 'Request'
	#NOTIFICATION_1xx        = '1xx'
	#NOTIFICATION_2xx        = '2xx'
	#NOTIFICATION_3xx        = '3xx'
	NOTIFICATION_STARTED    = 'Started'
	NOTIFICATION_COMPLETED  = 'Completed'
	NOTIFICATION_TERMINATED = 'Terminated'

	RESULT_COMPLETED        = 'Completed'
	RESULT_TIMEOUT_F        = 'TimeoutF'
	RESULT_TIMEOUT_J        = 'TimeoutJ'
	RESULT_TRANSPORT_ERROR  = 'TransportError'
	RESULT_CANCELLED        = 'Cancelled'

	CONFIG_TIMER_A = 1
	CONFIG_TIMER_B = 1
	CONFIG_TIMER_D = 1
	CONFIG_TIMER_E = 0.5
	CONFIG_TIMER_F = 4
	CONFIG_TIMER_G = 1
	CONFIG_TIMER_H = 1
	CONFIG_TIMER_J = 1
	CONFIG_TIMER_J = 0.5
	CONFIG_TIMER_K = 0.25

#Inform the TU (Send state to TU).
#Pass request to TU.
#Resend request to server.
#Resend response to client.
#Restart Timer E, G.
#Save request, response.
#Send ACK to server.
#Send request(INVITE) to server.
#Send response to client.
#Send response to the TU.
#Start Timer A, B, D, E, F, G, H, I, J.

# App message
#	Request
#	Response
# Message
#	Request
#	Response
#		1xx
#		2xx
#		3xx-6xx
# Timer
#	A - J
# Network Error
