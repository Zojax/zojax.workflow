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
import unittest, doctest
from zope import component
from zope.app.testing import setup
from zope.annotation.attribute import AttributeAnnotations

from zojax.workflow import state, info, workflow


def setUp(test):
    setup.placelessSetUp(True)
    setup.setUpTestAsModule(test, name='zojax.workflow.TESTS')

    component.provideAdapter(state.WorkflowState)
    component.provideAdapter(info.WorkflowInfo)
    component.provideHandler(workflow.initWorkflow)
    component.provideAdapter(AttributeAnnotations)
    component.provideAdapter(state.contentPermissionsMap,
                             name='workflow.state.permissions')

def tearDown(test):
    setup.placelessTearDown()
    setup.tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            './tests.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
