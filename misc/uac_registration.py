REREGISTRATION_RATIO = 0.75

class Registration(object):
	def __init__(self, user, contact, expires, timeout):
		self.user = user
		self.contact = contact
		self.expires = expires
		self.timeout = timeout
		self.timer = Timer(self.timeout, self.onTimeout)
		self.timer.start()

	def onTimeout(self):
		# FIXME: Will the timer get killed if this object is destroyed?
		self.user.registrationTimeout(self.contact)

	def __str__(self):
		return '[user:' + str(self.user) + ', contact: ' + str(self.contact.create()) + ', expires:' + str(self.expires) + ']'
