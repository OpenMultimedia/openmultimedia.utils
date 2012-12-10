# -*- coding: utf-8 -*-

import unittest2 as unittest


from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser

from openmultimedia.utils.viewlets import OpenMultimediaFooter

from openmultimedia.utils.testing import INTEGRATION_TESTING
from openmultimedia.utils.testing import FUNCTIONAL_TESTING


class FooterViewletTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        #generate test site structure
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.invokeFactory('Folder', 'folder2', title='Folder 2')
        self.portal.invokeFactory('Folder', 'folder3', title='Folder 3')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['folder1']
        #subfolders
        self.folder.invokeFactory('Folder', 'subfolder1', title='Sub Folder 1')
        self.folder.invokeFactory('Folder', 'subfolder2', title='Sub Folder 2')

    def test_footer_structure(self):
        view = OpenMultimediaFooter(self.portal, self.request, None, None)
        sections = view.get_footer_section()
        self.assertTrue(len(sections) == 3)
        self.assertTrue(len(sections[0]) == 2)
        self.assertTrue(len(sections[0][0]) == 2)
        #first level navigation
        self.assertTrue(sections[0][0][0] == 'Folder 1')
        self.assertTrue(sections[1][0][0] == 'Folder 2')
        self.assertTrue(sections[2][0][0] == 'Folder 3')
        #second level inside Folder 1
        #we have two elements
        self.assertTrue(len(sections[0][1]) == 2)
        #match the names
        self.assertTrue(len(sections[0][1][0]) == 2)
        self.assertTrue(sections[0][1][0][0] == 'Sub Folder 1')
        self.assertTrue(sections[0][1][1][0] == 'Sub Folder 2')

    @unittest.expectedFailure
    def test_util_links_viewlet(self):
        self.fail(NotImplemented)


class FooterFunctionalTest(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        #browserLogin(self.portal, self.browser)

    def test_live_signal_url(self):
        self.browser.open(self.portal.absolute_url())
        self.assertTrue('openmultimedia-sections-footer' in self.browser.contents)
