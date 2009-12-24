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
from zope import interface, component
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

from interfaces import InvalidTransitionError
from interfaces import IWorkflow, IState, ITransition
from interfaces import IWorkflowInfo, IWorkflowAware

from state import NullState


class Workflow(object):
    interface.implements(IWorkflow)

    def __init__(self, name, title, transitions, description=u''):
        self.name = name
        self.title = title
        self.description = description
        self.refresh(transitions)

    def _register(self, transition):
        for source in transition.source:
            transitions = self._sources.setdefault(source, {})
            transitions[transition.id] = transition

        self._id_transitions[transition.id] = transition

    def refresh(self, transitions):
        self._sources = {}
        self._id_transitions = {}
        for transition in transitions:
            self._register(transition)

        id_sources = {}
        for source in self._sources.keys():
            if source is not NullState:
                id_sources[source.id] = source

        self._id_sources = id_sources

        self._p_changed = True

    def getState(self, id, default=None):
        return self._id_sources.get(id, default)

    def getStates(self):
        return self._id_sources.values()

    def getTransitions(self, source, type=ITransition):
        try:
            if IState.providedBy(source):
                return [t for t in self._sources[source].values()
                        if type.providedBy(t)]
            else:
                return [t for t in
                        self._sources[self._id_sources[source]].values()
                        if type.providedBy(t)]
        except KeyError:
            return []

    def getTransition(self, source, transition_id):
        transition = self._id_transitions[transition_id]
        if not IState.providedBy(source):
            source = self.getState(source)

        if source not in transition.source:
            raise InvalidTransitionError

        return transition

    def getTransitionById(self, transition_id):
        return self._id_transitions[transition_id]


@component.adapter(IWorkflowAware, IObjectCreatedEvent)
def initWorkflow(object, event=None):
    info = IWorkflowInfo(object)
    info.fireAutomatic()
