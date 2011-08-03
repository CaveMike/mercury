#!/usr/bin/env python
from iron.dispatcher import Dispatcher
from iron.event import Event
from mercury.core import SipException
from mercury.header.header import SIP_CRLF
from mercury.message.message import Message
from mercury.message.message import MessageEvent
from mercury.message.message_assembler import DatagramReassembler
from mercury.message.message_assembler import StreamReassembler
from mercury.message.message_coder import MessageCoder
from mercury.network.netevent import NetError
from mercury.network.netevent import NetEvent
from mercury.network.network import Network
import logging
import unittest
from mercury.message.message_adapter import MessageAdapter

if __name__ == "__main__":
	logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
	unittest.main()
