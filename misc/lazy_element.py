#! /usr/bin/python
from carbon.helpers import *
from copy import copy
from iron.event import Event
from itertools import *
from mercury.header.element import IElement
from sys import modules
from UserString import MutableString
import logging
import inspect

class LazyElement2(object):
	def __init__( self, value = None ):
		pass


#===============================================================================
class LazyElement(object):
#FIXME: There are some issues with this class still.
#FIXME:	The	build and parse need to be intercepted from children.  Children should not implment build and parse, but a child-version of these.

#FIXME: After a call to build(), we should save the value in raw and set the state to PARSED.

	STATE_UNINITIALIZED = None
	STATE_INITIALIZED   = 1
	STATE_PARSING       = 2
	STATE_PARSED        = 3
	STATE_DIRTY         = 4

	def __init__( self, watched = None, value = None ):
		self.__watched = watched
		self.__raw = value
		self.__state = LazyElement.STATE_UNINITIALIZED

	def initDone( self ):
		if self.__raw:
			self.__state = LazyElement.STATE_INITIALIZED
		else:
			self.__state = LazyElement.STATE_PARSED

	def buildDone( self, value ):
		self.__raw = value
		self.__state = LazyElement.STATE_PARSED

	@nestedproperty
	def raw():
		doc = ""
		def fget( self ):
			return self.__raw
		return property( fget, None, None, doc )

	def __getattribute__( self, name ):
		#print '__getattribute__ ' + str(name)
		__watched = object.__getattribute__( self, '_LazyElement__watched' )
		if name not in __watched:
			#print 'Not watching ' + name
			return object.__getattribute__( self, name )

		__state = object.__getattribute__( self, '_LazyElement__state' )
		#print 'State: ' + str(__state) + '.'
		if __state == LazyElement.STATE_INITIALIZED:
			print 'Parsing ' + str(object.__getattribute__( self, '_LazyElement__raw' ))
			object.__setattr__( self, '_LazyElement__state', LazyElement.STATE_PARSING )
			self.parse( self.__raw )
			print 'Parsed ' + str(object.__getattribute__( self, '_LazyElement__raw' ))
			object.__setattr__( self, '_LazyElement__state', LazyElement.STATE_PARSED )

		return object.__getattribute__( self, name )

	def __setattr__( self, name, value ):
		#print '__setattr__ ' + str(name) + ', ' + str(value) + '.'
		try:
			__watched = object.__getattribute__( self, '_LazyElement__watched' )
			if name not in __watched:
				#print 'Not watching ' + name
				return object.__setattr__( self, name, value )
		except AttributeError:
			# __watched is being set in __init__().
			return object.__setattr__( self, name, value )

		__state = object.__getattribute__( self, '_LazyElement__state' )
		print 'State: ' + str(__state)
		if __state == LazyElement.STATE_INITIALIZED:
			print 'Parsing ' + str(object.__getattribute__( self, '_LazyElement__raw' ))
			object.__setattr__( self, '_LazyElement__state', LazyElement.STATE_PARSING )
			self.parse( self.__raw )
			print 'Parsed ' + str(object.__getattribute__( self, '_LazyElement__raw' ))
#			object.__setattr__( self, '_LazyElement__state', LazyElement.STATE_PARSED )
#		elif __state == LazyElement.STATE_PARSED:
#			# Ignore the inital sets in __init__() and parse().
#			object.__setattr__( self, '_LazyElement__state', LazyElement.STATE_DIRTY )
#			print 'State: ' + str(object.__getattribute__( self, '_LazyElement__state' ))

		object.__setattr__( self, '_LazyElement__state', LazyElement.STATE_DIRTY )

		return object.__setattr__( self, name, value )

	""" Overload the set operation to act as a string parse. """
	def __set__( self, obj, value ):
#FIXME: if type(value) == 'String'
		self.parse( value )

	""" Overload the string operator to build the header. """
	def __str__( self ):
		if self.__state < LazyElement.STATE_DIRTY:
			#print 'The element is not dirty.  Use the raw version.'
			return self.__raw

		return self.build()

	""" Overload the repr string operator to dump the element. """
	def __repr__( self ):
		return self.dump()

	""" Convert from string to element. """
	def parse( self, value ):
		raise SipException( 'Parse needs to be implemented by ' + str(self.__class__) + '.' )

	""" Convert from element to string. """
	def build( self ):
		raise SipException( 'Build needs to be implemented by ' + str(self.__class__) + '.' )

	""" Raise a SipException if the element is NOT valid. """
	def validate( self, thorough = False  ):
		raise SipException( 'Validation needs to be implemented by ' + str(self.__class__) + '.' )

	""" Create a string dump of the object's internal variables. """
	def dump( self ):
		raise SipException( 'Dump needs to be implemented by ' + str(self.__class__) + '.' )

class LazyObj(LazyElement):
	def __init__( self, value = None ):
		super( LazyObj, self ).__init__( watched = ('value', 'method'), value = value )
		self.value = None
		self.method = None
		self.xxx = False
		self.initDone()

	def __cmp__( self, other ):
		if self.value != other.value:
			return self.value.__cmp__( other.value )

		if self.method != other.method:
			return self.method.__cmp__( other.method )

		return 0

	def parse( self, value ):
		if value:
			(self.value, self.method ) = value.split( ' ', 1 )
			self.value = int(self.value)

	def build( self ):
		s = MutableString()

		s += str(self.value)
		s += ' '
		s += str(self.method)

		return str(s)

	def validate( self, thorough = False  ):
		return self.method and self.value

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.raw) + '\'' + ', '
		s += 'value:\'' + str(self.value) + '\'' + ', '
		s += 'method:\'' + str(self.method) + '\'' + ', '
		s += ']'

		return str(s)

class TestLazyObj(unittest.TestCase):
	def runTest( self ):
		cseq = LazyObj( '7 OPTIONS' )

		print cseq.xxx

		assert( cseq.raw == '7 OPTIONS' )
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_INITIALIZED )

		print 'Force parse'
		print cseq.method
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_PARSED )

		print 'Make dirty'
		cseq.method = 'UPDATE'
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_DIRTY )
		assert( cseq.method == 'UPDATE' )

		del cseq.method
		try:
			cseq.method
		except AttributeError:
			pass

		try:
			cseq.dummy
		except AttributeError:
			pass

		print '#2'
		cseq = LazyObj()
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_PARSED )
		print 'Make dirty'
		cseq.method = 'REGISTER'
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_DIRTY )
		print cseq

		print '#3'
		cseq = LazyObj( '' )
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_PARSED )
		print 'Make dirty'
		cseq.method = 'REGISTER'
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_DIRTY )
		print cseq

		print '#4'
		cseq = LazyObj( '7 SUBSCRIBE' )
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_INITIALIZED )
		print 'Force parse then make dirty'
		cseq.method = 'REGISTER'
		print '----', ( object.__getattribute__( cseq, '_LazyElement__state' ) )
		assert( object.__getattribute__( cseq, '_LazyElement__state' ) == LazyElement.STATE_DIRTY )
		print cseq

#===============================================================================
class LazyCSeq(IElement):
	def __init__( self, value = None ):
		super( LazyCSeq, self ).__init__( value )
		self._state = LazyElement.STATE_INITIALIZED
		self.__value = None
		self.__method = None
		self.__dict__['__initialized'] = True

	@nestedproperty
	def method():
		doc = ""
		def fget( self ):
			if self._state == LazyElement.STATE_INITIALIZED:
				self.parse( self.raw )

			return self.__method
		def fset( self, value ):
			if self._state == LazyElement.STATE_INITIALIZED:
				self.parse( self.raw )

			self.__method = value
			self._state = LazyElement.STATE_DIRTY

		def fdel( self ):
			if self._state == LazyElement.STATE_INITIALIZED:
				self.parse( self.raw )

			self.__method = None
			self._state = LazyElement.STATE_DIRTY

		return property( fget, fset, fdel, doc )

	@nestedproperty
	def value():
		doc = ""
		def fget( self ):
			if self._state == LazyElement.STATE_INITIALIZED:
				self.parse( self.raw )

			return self.__value
		def fset( self, value ):
			if self._state == LazyElement.STATE_INITIALIZED:
				self.parse( self.raw )

			self.__value = value
			self._state = LazyElement.STATE_DIRTY

		def fdel( self ):
			if self._state == LazyElement.STATE_INITIALIZED:
				self.parse( self.raw )

			self.__value = None
			self._state = LazyElement.STATE_DIRTY

		return property( fget, fset, fdel, doc )

	def parse( self, value ):
		self._state = LazyElement.STATE_PARSING
		if value:
			(self.__value, self.__method ) = value.split( ' ', 1 )
			self.__value = int(self.__value)
			self._state = LazyElement.STATE_PARSED

	def build( self ):
		if self._state < LazyElement.STATE_DIRTY:
			return self.raw

		s = MutableString()

		s += str(self.value)
		s += ' '
		s += str(self.method)

		return str(s)

	def validate( self, thorough = False  ):
		pass

	def dump( self ):
		s = MutableString()

		s += '['
		s += 'raw:\'' + str(self.__raw) + '\'' + ', '
		s += 'watched:\'' + str(self.__watched) + '\'' + ', '
		s += 'state:\'' + str(self._state) + '\'' + ', '
		s += 'value:\'' + str(self.__value) + '\'' + ', '
		s += 'method:\'' + str(self.__method) + '\'' + ', '
		s += ']'

		return str(s)

class Dirty1(unittest.TestCase):
	def unTest( self ):
		self.TestUri( 'sip:host', 'sip:1234@host' )

	def TestUri( self, i, o = None ):
		if not o:
			o = i
		#print i
		class LazySipUri(SipUri, LazyElement): pass
		uri = LazySipUri( i )
		assert( object.__getattribute__( uri, '_state' ) == LazyElement.STATE_INITIALIZED )
		#print object.__getattribute__( uri, '_state' )
		#print uri.__dict__

		#print '\n\ntrigger parse...'
		#print str(uri.host)
		assert( object.__getattribute__( uri, '_state' ) == LazyElement.STATE_PARSED )
		#print uri.__dict__

		#print '\n\ndo build...'
		#print str(uri)

		#print '\n\ntrigger dirty...'
		uri.user = '1234'
		assert( object.__getattribute__( uri, '_state' ) == LazyElement.STATE_DIRTY )
		#print uri.__dict__
		#print uri.user

		#print '\n\ndo another build...'
		#print str(uri)

		#print uri.dump()
		#print str(uri)
		#assert( uri.dirty )
		assert( o == str(uri) )

class Dirty2(unittest.TestCase):
	def runTest( self ):

		cseq = LazyCSeq( '7 OPTIONS' )

		assert( cseq.raw == '7 OPTIONS' )
		assert( object.__getattribute__( cseq, '_state' ) == LazyElement.STATE_INITIALIZED )

		cseq.method
		assert( object.__getattribute__( cseq, '_state' ) == LazyElement.STATE_PARSED )

		cseq.method = 'UPDATE'
		assert( object.__getattribute__( cseq, '_state' ) == LazyElement.STATE_DIRTY )
		assert( cseq.method == 'UPDATE' )

		del cseq.method
		assert( not cseq.method )

if __name__ == "__main__":
	unittest.main()
