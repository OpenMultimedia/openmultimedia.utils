# -*- coding: utf-8 -*-

import unittest2 as unittest

import logging

#from AccessControl import Unauthorized

from Products.ATContentTypes.lib import constraintypes

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from openmultimedia.utils.setuphandlers import (
#    create_default_section_link,
    create_menu_item,
#    create_section,
#    set_one_state_workflow_policy,
    )

from openmultimedia.utils.config import PROJECTNAME
from openmultimedia.utils.testing import INTEGRATION_TESTING


class SetupHandlersTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.wt = getattr(self.portal, 'portal_workflow')
        self.logger = logging.getLogger(PROJECTNAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _review_state(self, item):
        review_state = self.wt.getInfoFor(item, 'review_state')
        return review_state

    @unittest.expectedFailure
    def test_import_initial(self):
        #import_initial()
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_apply_initial_profile(self):
        #apply_initial_profile()
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_run_upgrade_steps(self):
        #run_upgrade_steps()
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_set_one_state_workflow_policy(self):
        self.fail(NotImplemented)

    def test_create_menu_item(self):
        # test with default values
        create_menu_item(self.portal, "Foo")
        self.assertTrue('foo' in self.portal.objectIds())

        item = self.portal['foo']

        self.assertEqual(item.portal_type, 'Folder')
        self.assertEqual(item.getConstrainTypesMode(), constraintypes.ENABLED)

        # any attemp to create anything else but Topics must fail
        self.assertRaises(ValueError, item.invokeFactory, 'Document', 'bar')

        # by default the object is not excluded from navigation
        self.assertFalse(item.getExcludeFromNav())

        # TODO: enhance tests

    @unittest.expectedFailure
    def test_create_section(self):
        #create_section()
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_create_default_section_link(self):
        #create_default_section_link()
        self.fail(NotImplemented)
