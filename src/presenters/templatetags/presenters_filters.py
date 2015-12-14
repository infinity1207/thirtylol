# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter
def abbreviation_number(value):
	"""
	一万以内的数值原样输出，超过一万的数值以万为单位，保留一位小数点输出
	例：134567将输出为13.4万
	"""
	try:
		f_value = float(value)
		if f_value < 10000:
			return value
		return u"%.1f万" % (f_value / 10000)
	except:
		return value

@register.filter
def modulo(value, arg):
	try:
		i_value = int(value)
		i_arg = int(arg)
		return i_value % i_arg
	except:
		return value
