#!/usr/bin/env python
from copy import copy
from mercury.core import SipException
from carbon.helpers import nestedproperty
from UserString import MutableString
import logging

class IElement(object):
	def __init__( self, value = None ):
		self.__raw = value

	@nestedproperty
	def raw():
		doc = ""
		def fget( self ):
			return self.__raw
		return property( fget, None, None, doc )

	""" Overload the set operation to act as a string parse. """
	def __set__( self, obj, value ):
		self.parse( value )

	""" Overload the string operator to build the element. """
	def __str__( self ):
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

class Params(object):
	@staticmethod
	def __cmp__( params, kparams, otherParams, otherKparams ):
		n = kparams.__cmp__( otherKparams )
		if n != 0:
			return n

		l0 = copy( params )
		l0.sort()
		l1 = copy( otherParams )
		l1.sort()
		if l0 != l1:
			return 1

		return 0

	@staticmethod
	def parse( params, kparams, value ):
		lvalue = value

		n = value.find( ';' )
		if n >= 0:
			lvalue = value[:n]
			rvalue = value[n+1:]
			rvalue = rvalue.replace( ',', ';' )

			allparams = rvalue.split( ';' )
			for param in allparams:
				n = param.find( '=' )
				if n >= 0:
					v = param[n+1:].strip()
					k = param[:n].strip()
					kparams[k] = v
				else:
					params.append( param.strip() )

		return lvalue

	@staticmethod
	def build( params, kparams ):
		s = MutableString()

		for param in params:
			s += ';'
			s += param

		for (key, value) in kparams.iteritems():
			s += ';'
			s += key
			s += '='
			s += value

		return str(s)

	@staticmethod
	def validate( params, kparams, thorough = False  ):
		pass

	@staticmethod
	def dump( params, kparams ):
		s = MutableString()

		s += '['
		s += 'params:\'' + str(params) + '\'' + ', '
		s += 'kparams:\'' + str(kparams) + '\'' + ', '
		s += ']'

		return str(s)

class HParams(object):
	@staticmethod
	def __cmp__( hparams, hkparams, otherHparams, otherHkparams ):
		n = hkparams.__cmp__( otherHkparams )
		if n != 0:
			return n

		l0 = copy( hparams )
		l0.sort()
		l1 = copy( otherHparams )
		l1.sort()
		if l0 != l1:
			return 1

		return 0

	@staticmethod
	def parse( hparams, hkparams, value ):
		lvalue = value

		n = value.find( '?' )
		if n >= 0:
			rvalue = value[n+1:]
			lvalue = value[:n]

			allparams = rvalue.split( '&' )
			for param in allparams:
				n = param.find( '=' )
				if n >= 0:
					v = param[n+1:]
					k = param[:n]
					hkparams[k] = v
				else:
					hparams.append( param )

		return lvalue

	@staticmethod
	def build( hparams, hkparams ):
		s = MutableString()

		hparamprefix = '?'
		for hparam in hparams:
			s += hparamprefix
			s += hparam

			hparamprefix = '&'

		for (key, value) in hkparams.iteritems():
			s += hparamprefix
			s += key
			s += '='
			s += value

			hparamprefix = '&'

		return str(s)

	@staticmethod
	def validate( hparams, hkparams, thorough = False  ):
		pass

	@staticmethod
	def dump( hparams, hkparams ):
		s = MutableString()

		s += '['
		s += 'hparams:\'' + str(hparams) + '\'' + ', '
		s += 'hkparams:\'' + str(hkparams) + '\'' + ', '
		s += ']'

		return str(s)

