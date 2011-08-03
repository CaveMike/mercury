#!/usr/bin/env python
from mercury.message.container import Container

class ApplicationSimpleMessageSummaryBody(Container):
	def __init__( self, headers, body ):
		super( ApplicationSimpleMessageSummaryBody, self ).__init__( body )

