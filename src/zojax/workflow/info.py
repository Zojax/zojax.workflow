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
from zope import event, interface, component
from zope.component.interfaces import ObjectEvent
from zope.lifecycleevent import ObjectModifiedEvent

from interfaces import IWorkflow, IWorkflowState, IWorkflowInfo
from interfaces import ITransition, IWorkflowAware, IWorkflowTransitionEvent
from interfaces import IManualTransition, IAutomaticTransition
from interfaces import NoWorkflowAvailableError, ConditionFailedError


class WorkflowInfo(object):
    component.adapts(IWorkflowAware)
    interface.implements(IWorkflowInfo)

    def __init__(self, context):
        self.context = context
        self.workflow = IWorkflow(context, None)
        if self.workflow is None:
            raise NoWorkflowAvailableError()

        self.state = IWorkflowState(context)
        self.currState = self.state.getState()

    def fireTransition(self, transition, comment=u''):
        context = self.context

        if not ITransition.providedBy(transition):
            transition = self.workflow.getTransition(self.currState, transition)

        # check transition condition
        transition.check(context)

        # perform action
        transition.action(self.workflow, context)

        # change state of context
        state = IWorkflowState(context)
        newState = state.setState(transition.destination, comment=comment)

        if newState:
            event.notify(
                WorkflowTransitionEvent(
                    context, self.currState, newState, transition, comment))

        # send modified event for original or new object
        event.notify(ObjectModifiedEvent(context))

    def fireAutomatic(self):
        for transition in self.getAutomaticTransitions():
            try:
                self.fireTransition(transition)
            except ConditionFailedError:
                # if condition failed, that's fine, then we weren't
                # ready to fire yet
                pass
            else:
                # if we actually managed to fire a transition,
                # we're done with this one now.
                return

    def getTransitions(self):
        context = self.context

        return [trans for trans in self.workflow.getTransitions(
                self.state.getState(), IManualTransition)
                if trans.isAvailable(context)]

    def getAutomaticTransitions(self):
        return self.workflow.getTransitions(
            self.state.getState(), IAutomaticTransition)


class WorkflowTransitionEvent(ObjectEvent):
    interface.implements(IWorkflowTransitionEvent)

    def __init__(self, object, source, destination, transition, comment):
        super(WorkflowTransitionEvent, self).__init__(object)
        self.source = source
        self.destination = destination
        self.transition = transition
        self.comment = comment
