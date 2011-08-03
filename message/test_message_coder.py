#!/usr/bin/env python
import logging
import unittest
from mercury.message.message_coder import MessageCoder

class TestMessageCoder(unittest.TestCase):
	def runTest( self ):

		packet = '' \
'REGISTER sip:sip.example.com SIP/2.0\r\n' \
'Via: SIP/2.0/UDP 192.168.1.1:5060;rport;branch=z9hG4bK58790139-438475846\r\n' \
'Max-Forwards: 70\r\n' \
'Allow: INVITE,BYE,CANCEL,ACK,INFO,PRACK,OPTIONS,SUBSCRIBE,NOTIFY,PUBLISH,MESSAGE,REFER,REGISTER,UPDATE\r\n' \
'Supported: path,replaces,norefersub\r\n' \
'User-Agent: IMS Phone 49\r\n' \
'From: <sip:1@sip.example.com>;tag=UA_58790139-438475847\r\n' \
'To: <sip:1@sip.example.com>\r\n' \
'Call-ID: 58790139-438475845\r\n' \
'CSeq: 1 REGISTER\r\n' \
'Expires: 3600\r\n' \
'Contact: 1<sip:1@192.168.1.1:5060;transport=udp>;expires=3600\r\n' \
'Authorization: Digest username="1",realm="sip.example.com",nonce="",uri="sip:sip.example.com",response=""\r\n' \
'Content-Length: 0\r\n' \
'\r\n'

		mc = MessageCoder()
		print mc.decode( packet )

		print mc.encode( packet )

if __name__ == '__main__':
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()

