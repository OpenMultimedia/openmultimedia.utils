# -*- coding: utf-8 -*-

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.nitf
        self.loadZCML(package=collective.nitf)
        import openmultimedia.utils
        self.loadZCML(package=openmultimedia.utils)
        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.nitf:default')

        # Set default workflow chains for tests
        wf = portal['portal_workflow']
        types = (
            'collective.nitf.content',
            'Collection',
            'Folder',
        )
        wf.setChainForPortalTypes(types, 'simple_publication_workflow')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='openmultimedia.utils:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='openmultimedia.utils:Functional',
)


def browserLogin(portal, browser, username=None, password=None):
    handleErrors = browser.handleErrors
    try:
        browser.handleErrors = False
        browser.open(portal.absolute_url() + '/login_form')
        if username is None:
            username = TEST_USER_NAME
        if password is None:
            password = TEST_USER_PASSWORD
        browser.getControl(name='__ac_name').value = username
        browser.getControl(name='__ac_password').value = password
        browser.getControl(name='submit').click()
    finally:
        browser.handleErrors = handleErrors


def createObject(context, _type, id, delete_first=False,
                 check_for_first=False, **kwargs):
    if delete_first and id in context.objectIds():
        context.manage_delObjects([id])
    if not check_for_first or id not in context.objectIds():
        return context[context.invokeFactory(_type, id, **kwargs)]

    return context[id]
