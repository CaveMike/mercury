RESUBSCRIBE_RATIO = 0.75

EVENT_PACKAGE_MESSAGE_SUMMARY = 'message-summary'
EVENT_PACKAGE_CONFERENCE = 'conference'
EVENT_PACKAGE_SIP_PROFILE = 'sip-profile'
EVENT_PACKAGE_DIALOG_INFO = 'dialog-info'
EVENT_PACKAGE_REG_INFO = 'reginfo-info'
EVENT_PACKAGE_PRESENCE = 'presence'
EVENT_PACKAGE_REFER = 'refer'
EVENT_PACKAGE_WATCHERINFO = 'winfo'
EVENT_PACKAGE_MERCURY = 'mercury'

class SubscriptionSource(object):
	def isSubscribable(self, event, type, subtype):
		return False

	def subscribe(self, event, type, subtype):
		return None

	def getData(self, type, subtype, complete=True):
		return None
