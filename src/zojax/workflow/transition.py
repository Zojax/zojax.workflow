##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface
from zope.security import checkPermission
from zope.security.checker import CheckerPublic
from zope.security.interfaces import Unauthorized

from interfaces import ConditionFailedError
from interfaces import ITransition, IManualTransition, IAutomaticTransition


def NullCondition(context):
    return True


def NullAction(workflow, context):
    pass


class RolesCondition(object):

    def __init__(self, roles):
        self.roles = roles

    def __call__(self, wf, context):
        pass


class Transition(object):
    interface.implements(ITransition)

    def __init__(self, id, title, source, destination,
                 description = u'',
                 condition = NullCondition,
                 action = NullAction,
                 permission = CheckerPublic,
                 **user_data):
        self.id = id
        self.title = title
        self.source = source
        self.destination = destination
        self.description = description
        self.condition = condition
        self.action = action
        self.permission = permission
        self.user_data = user_data

    def __cmp__(self, other):
        return cmp(self.order, other.order)

    def check(self, context):
        if not checkPermission(self.permission, context):
            raise Unauthorized(
                context, 'transition: %s' % self.id, self.permission)

        if not self.condition(context):
            raise ConditionFailedError()

    def isAvailable(self, context):
        if not checkPermission(self.permission, context):
            return False

        if not self.condition(context):
            return False

        return True


class ManualTransition(Transition):
    interface.implements(IManualTransition)


class AutomaticTransition(Transition):
    interface.implements(IAutomaticTransition)
