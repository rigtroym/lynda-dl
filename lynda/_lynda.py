#!/usr/bin/python
# -*- coding: utf-8 -*-

from ._internal import InternLyndaCourse as Lynda


def course(url, username='', password='', organization='', cookies='', basic=True, callback=None):
    """Returns lynda course instance.

    @params:
        url      : Lynda course url required : type (string).
        username : Lynda email account required : type (string).
        password : Lynda account password required : type (string)
        organization : Lynda organization name optional : type (string)
    """
    return Lynda(url, username, password, organization, cookies, basic, callback)