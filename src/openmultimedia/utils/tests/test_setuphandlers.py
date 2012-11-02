# -*- coding: utf-8 -*-

import unittest2 as unittest

import logging

from AccessControl import Unauthorized

from Products.ATContentTypes.lib import constraintypes

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from openmultimedia.utils.setuphandlers import (
    create_default_section_link,
    create_menu_item,
#    create_section,
    set_one_state_workflow_policy,
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

    def test_set_one_state_workflow_policy(self):
        self.portal.invokeFactory('Folder', 'test')
        obj = self.portal['test']
        state = self._review_state(obj)
        self.assertEqual(state, 'private')

        set_one_state_workflow_policy(obj, self.logger)
        self.wt.updateRoleMappings()

        state = self._review_state(obj)
        # XXX: we need to test this is the one state workflow
        self.assertEqual(state, 'published')

    def test_create_menu_item(self):
        # test with default values
        create_menu_item(self.portal, "Test")
        self.assertTrue('test' in self.portal.objectIds())

        item = self.portal['test']

        self.assertEqual(item.portal_type, 'Folder')
        self.assertEqual(item.getConstrainTypesMode(), constraintypes.ENABLED)

        # by default a menu item can only contain Folders
        allowed_types = [t.getId() for t in item.allowedContentTypes()]
        self.assertEqual(allowed_types, ['Folder'])
        try:
            item.invokeFactory('Folder', 'foo')
        except Unauthorized:
            self.fail()

        # any attemp to create anything else but Folder must fail
        self.assertRaises(ValueError, item.invokeFactory, 'Document', 'foo')

        # by default the object is not excluded from navigation
        self.assertFalse(item.getExcludeFromNav())

        # now, we overwrite the configuraton of the object
        create_menu_item(self.portal, "Test", ['Document'], True)

        allowed_types = [t.getId() for t in item.allowedContentTypes()]
        self.assertEqual(allowed_types, ['Document'])
        self.assertTrue(item.getExcludeFromNav())

    @unittest.expectedFailure
    def test_create_section(self):
        #create_section()
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_create_default_section_link(self):
        create_default_section_link()
        self.fail(NotImplemented)
