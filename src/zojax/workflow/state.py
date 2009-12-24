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
from pytz import utc
from datetime import datetime
from persistent.list import PersistentList

from zope import interface, component
from zope.proxy import removeAllProxies
from zope.annotation.interfaces import IAnnotations
from zope.security.management import getInteraction
from zope.securitypolicy.interfaces import IRolePermissionMap

from zojax.permissionsmap.interfaces import IPermissionsMap

from interfaces import ANNOTATION_KEY
from interfaces import IState, IWorkflow, IWorkflowState, IWorkflowAware


class State(object):
    interface.implements(IState)

    def __init__(self, id, title, description=u'', permissionsmap=''):
        self.id = id
        self.title = title
        self.description = description
        self.permissionsmap = permissionsmap

    def afterTransition(self, context, oldState, workflow=None):
        pass

    def __str__(self):
        return self.title or self.id


@component.adapter(IWorkflowAware)
@interface.implementer(IRolePermissionMap)
def contentPermissionsMap(content, queryUtility=component.queryUtility):
    state = IWorkflowState(content, None)
    if state is not None:
        state = state.getState()
        if state.permissionsmap:
            return queryUtility(IPermissionsMap, state.permissionsmap)


NullState = State(None, 'Unknown')


class WorkflowState(object):
    component.adapts(IWorkflowAware)
    interface.implements(IWorkflowState)

    def __init__(self, context):
        self.context = removeAllProxies(context)
        self.workflow = IWorkflow(self.context, None)
        self.annotations = IAnnotations(self.context)

    def _get_history(self):
        info = self.annotations.get(ANNOTATION_KEY)
        if info is None:
            info = PersistentList()
            self.annotations[ANNOTATION_KEY] = info

        return info

    def setState(self, state, **kwargs):
        old_state = self.getState()
        if state != old_state:
            info = self._get_history()

            kwargs['state'] = state.id
            kwargs['time'] = datetime.now(utc)

            actor = []
            for participation in getInteraction().participations:
                actor.append(participation.principal.id)

            kwargs['actor'] = tuple(actor)
            info.append(kwargs)

            state.afterTransition(self.context, old_state, self.workflow)
            return state

    def getState(self):
        if self.workflow is None:
            return NullState

        try:
            state = self.workflow.getState(
                self.annotations[ANNOTATION_KEY][-1]['state'])
            if state is not None:
                return state
        except (KeyError, IndexError):
            pass
        return NullState

    def time(self, state):
        if IState.providedBy(state):
            state = state.id

        history = self._get_history()

        for idx in range(len(history), 0, -1):
            item = history[idx-1]
            if item['state'] == state:
                return item['time']

        return None

    def history(self):
        return list(self._get_history())
