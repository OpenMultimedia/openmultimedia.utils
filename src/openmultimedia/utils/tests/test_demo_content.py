# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from openmultimedia.utils.demo_content import (
    generate_sentence,
    generate_sentences,
    generate_paragraphs,
    generate_keywords,
    create_article,
)

from openmultimedia.utils.testing import INTEGRATION_TESTING


class SetupHandlersTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_generate_sentence(self):
        self.assertNotEqual(generate_sentence(), '')

    def test_generate_sentences(self):
        s = generate_sentences(10)
        self.assertNotEqual(s, '')
        self.assertTrue(s.count('.', 10))

    def test_generate_paragraphs(self):
        self.assertNotEqual(generate_paragraphs(1), '')

    @unittest.expectedFailure
    def test_generate_text(self):
        self.fail(NotImplemented)

    def test_generate_keywords(self):
        keywords = generate_keywords()
        self.assertTrue(len(keywords) <= 5)

    @unittest.expectedFailure
    def test_generate_image(self):
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_random_genre(self):
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_random_section(self):
        self.fail(NotImplemented)

    # FIXME: raises ValueError because we have no genres registered on test
    @unittest.expectedFailure
    def test_create_article(self):
        create_article(self.folder)

    @unittest.expectedFailure
    def test_generate_polls(self):
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_generate_galeries(self):
        self.fail(NotImplemented)

    @unittest.expectedFailure
    def test_generate(self):
        self.fail(NotImplemented)
