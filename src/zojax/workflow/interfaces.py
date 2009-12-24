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
""" workflow package based on hurry.workflow

$Id$
"""
from zope import schema, interface
from zope.component.interfaces import IObjectEvent
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zojax.workflow')

ANNOTATION_KEY = 'zojax.workflow'


class WorkflowException(Exception):
    """ base workflow exception """


class NoWorkflowAvailableError(WorkflowException):
    pass


class InvalidTransitionError(WorkflowException):
    pass


class NoTransitionAvailableError(InvalidTransitionError):
    pass


class AmbiguousTransitionError(InvalidTransitionError):
    pass


class ConditionFailedError(WorkflowException):
    pass


class IWorkflowAware(interface.Interface):
    """ marker interface for workflow aware objects """


class IWorkflow(interface.Interface):
    """Defines workflow in the form of transition objects.

    Defined as a utility.
    """

    title = schema.TextLine(
        title = _(u'Title'),
        required = True)

    description = schema.Text(
        title = u'Descripiton',
        description = u'Workflow description, help information for end user.',
        required  = False)

    def refresh(transitions):
        """Refresh workflow completely with new transitions."""

    def getState(id):
        """ get state object by it's id """

    def getStates():
        """ get all states objects """

    def getTransitions(source, type):
        """Get all transitions from source."""

    def getTransition(source, transition_id):
        """Get transition with transition_id given source state.

        If the transition is invalid from this source state,
        an InvalidTransitionError is raised.
        """

    def getTransitionById(transition_id):
        """Get transition with transition_id."""


class IState(interface.Interface):
    """ state object """

    id = schema.TextLine(
        title = u'State id',
        required = True)

    title = schema.TextLine(
        title = u'State title',
        required = True)

    description = schema.TextLine(
        title = u'State description',
        default = u'',
        required = False)

    permissionsmap = interface.Attribute('Permissions map')

    def afterTransition(context, old_state, workflow):
        """ after transition handler """


class ITransition(interface.Interface):
    """ workflow transition """

    id = interface.Attribute('id')
    title = interface.Attribute('title')
    source = interface.Attribute('source')
    destination = interface.Attribute('destination')
    description = interface.Attribute('description')
    condition = interface.Attribute('condition')
    action = interface.Attribute('action')
    permission = interface.Attribute('permission')
    user_data = interface.Attribute('user_data')

    def check(context):
        """ check transaction for context, raise exception """

    def isAvailable(context):
        """ is transaction available for context, return bool """


class IManualTransition(ITransition):
    """ manual transition """


class IAutomaticTransition(ITransition):
    """ automatic transition """


class IWorkflowState(interface.Interface):
    """Store state on workflowed objects.

    Defined as an adapter.
    """

    def setState(state, **kwargs):
        """Set workflow state for this object. """

    def getState():
        """Return workflow state (IState) of this object. """

    def time(state):
        """ return time of state """

    def history():
        """ return workflow history """


class IWorkflowInfo(interface.Interface):
    """Get workflow info about workflowed object, and drive workflow.

    Defined as an adapter.
    """

    def fireTransition(transitionId, comment=u''):
        """Fire a transition for the context object.

        There's an optional comment parameter that contains some
        opaque object that offers a comment about the transition.
        This is useful for manual transitions where users can motivate
        their actions.
        """

    def fireAutomatic():
        """Fire automatic transitions if possible by condition."""

    def getTransitions():
        """Returns list of valid manual transitions.

        These transitions have to have a condition that's True.
        """

    def getAutomaticTransitions():
        """Returns list of possible automatic transitions.

        Condition is not checked.
        """


class IWorkflowTransitionEvent(IObjectEvent):

    source = interface.Attribute('Original state or None if initial state')

    destination = interface.Attribute('New state')

    transition = interface.Attribute('Transition that was fired or None if initial state')

    comment = interface.Attribute('Comment that went with state transition')
