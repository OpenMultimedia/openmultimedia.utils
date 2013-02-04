# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import hashlib
# Zope imports
from AccessControl import getSecurityManager

from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema import TextLine
from zope.schema import List
from zope.schema import DottedName
from Acquisition import aq_inner
from five import grok

# Plone imports
from plone.app.portlets.portlets.navigation import Assignment
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder
from plone.i18n.normalizer import idnormalizer

from plone.registry.interfaces import IRegistry

# Local imports
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


grok.templatedir("viewlets")


class OpenMultimediaFooter(grok.Viewlet):
    grok.context(Interface)

    grok.name(u"openmultimedia.footer")
    grok.require("zope2.View")
    grok.template("footer")
    grok.viewletmanager(IPortalFooter)

    def get_footer_section(self):
        """
        """
        self.context = aq_inner(self.context)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.root_path = portal_state.navigation_root_path()
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        path = self.root_path

        # first we get root items
        query['path'] = {'query': path, 'depth': 1}
        query['sort_on'] = 'getObjPositionInParent'
        level_one = [(i.Title, i.getURL()) for i in catalog(**query)
                     if not i.exclude_from_nav]

        # now we get root items and items inside them
        query['path'] = {'query': path, 'depth': 2}
        level_two = [(i.Title, i.getURL()) for i in catalog(**query)
                     if not i.exclude_from_nav]

        footer = []
        for i in level_one:
            subsections = []
            for j in level_two:
                if i[1] == j[1]:  # item is duplicated; skip it
                    continue
                if i[1] in j[1]:  # item is inside; add it
                    subsections.append(j)

            footer.append((i, subsections))
        return footer


class DropdownQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query suitable for a dropdownmenu"""

    def __init__(self, context):
        NavtreeQueryBuilder.__init__(self, context)
        portal_path = context.portal_url.getPortalObject().getPhysicalPath()
        portal_len = len(portal_path)
        context_url = context.getPhysicalPath()
        self.query['path'] = {'query': '/'.join(context_url[:(portal_len + 1)]),
                              'navtree_start': 1,
                              'depth': 2}


class SubSectionList(grok.Viewlet):
    grok.context(Interface)
    grok.name(u"openmultimedia.subsection")
    grok.require("zope2.View")
    grok.template("sub_section_list")
    grok.viewletmanager(IPortalHeader)

    def update(self):
        self.navroot_path = getNavigationRoot(self.context)
        self.data = {}

        tab = aq_inner(self.context)

        if hasattr(self.context, 'section') and getattr(self.context, 'portal_type', None) == 'collective.nitf.content':
            section = self.context.section
            oid = idnormalizer.normalize(section, 'es')
            news_folder = getattr(self.context.portal_url, 'noticias', None)
            if news_folder:
                tab = getattr(news_folder, oid, None)

        #XXX this should be generalized... this hardcoded cases are so so lame.. sorry
        # if  getattr(self.context, 'portal_type', None) == 'collective.polls.poll':
        #     polls_folder = getattr(self.context.portal_url, 'encuestas', None)
        #     if polls_folder:
        #         tab = polls_folder

        if not tab:
            return

        strategy = getMultiAdapter((tab, Assignment(root=self.navroot_path)),
                                   INavtreeStrategy)
        queryBuilder = DropdownQueryBuilder(tab)
        query = queryBuilder()

        if query['path']['query'] != self.navroot_path:
            self.data = buildFolderTree(tab, obj=tab, query=query, strategy=strategy)


class IUtilLinks(Interface):
    """ Interface for the links registry
    """
    links = List(title=u"Links",
                 value_type=DottedName(title=u"Links ID"))


class IUtilLink(Interface):
    """ Interface for each link
    """

    text = TextLine(title=u"Text",
                    description=u"The text you want the link to show")
    uri = TextLine(title=u"URI",
                   description=u"The URI where the link redirects. Use "
                               "{portal}/ at the beginning to replace it "
                               "with the site root or {relative}/ to make "
                               "it relative to context.")
    css = TextLine(title=u"CSS",
                   description=u"additional css clases you want to be "
                               "rendered")
    condition = TextLine(title=u"Condition",
                         description=u"A condition that needs to be true "
                                     "in order for the link to be rendered")
    permission = TextLine(title=u"Permission",
                          description=u"A permission the current user should "
                                      "have, so the link will be rendered.")


class OpenMultimediaUtilLinks(ViewletBase):
    """ This viewlet will render a list of links stored in the registry
    """

    index = ViewPageTemplateFile('viewlets/utillinks.pt')

    def get_links(self):
        """ Here we get the links from the registry
        """

        registry = getUtility(IRegistry)
        try:
            linksregistry = registry.forInterface(IUtilLinks)
        except KeyError:
            linksregistry = None

        links = []
        if linksregistry:
            for link_id in linksregistry.links:
                links.append(registry.forInterface(IUtilLink, prefix=link_id))

        return links

    def should_render(self, link):
        """ This method will evaluate the condition for the link.
        It returns True if there's no condition
        """

        pm = getToolByName(self.context, 'portal_membership')

        context = self.context
        context  # PyFlakes
        request = self.request
        request  # PyFlakes
        portal = self.context.portal_url.getPortalObject()
        portal  # PyFlakes
        auth_member = pm.getAuthenticatedMember()
        auth_member  # PyFlakes
        if pm.isAnonymousUser() == 0:
            is_anon = False
        else:
            is_anon = True
        is_anon  # PyFlakes

        result = True
        if link.condition is not None:
            result = eval(link.condition)

        return result

    def is_member_allowed(self, link):
        """ This method will check if the current member
        has the requested permission.
        If no permission was requested, then return True
        """
        result = True
        if link.permission is not None:
            sm = getSecurityManager()
            allowed = sm.checkPermission(link.permission, self.context)
            if allowed is None or allowed == 0:
                result = False

        return result

    def get_uri(self, link):
        if link.uri is not None:
            if link.uri.startswith('{portal}'):
                portal_obj = self.context.portal_url.getPortalObject()
                portal_url = portal_obj.absolute_url()
                uri = "%s/%s" % (portal_url, link.uri[9:])

            elif link.uri.startswith('{relative}'):
                context_url = self.context.absolute_url()
                uri = "%s/%s" % (context_url, link.uri[11:])

            else:
                uri = link.uri

            return uri


class IMultimediaAdminJS(Interface):
    """ Interface for the the multimedia admin js
    """
    url = TextLine(title=u"url",
                   description=u"The url of the javascript forthe multimedia admin")

    path = TextLine(title=u"path",
                    description=u"path to the multimedia admin")

    secret = TextLine(title=u"secret key",
                      description=u"secret key to be able to connect to the multimedia admin")


class OpenMultimediaAdminJS(ViewletBase):
    """ This viewlet will render the js that connects to the admin interface for openmultimedia
    """

    index = ViewPageTemplateFile('viewlets/openmultimediaadminjs.pt')

    def js(self):
        """ Here we get the links from the registry
        """
        registry = getUtility(IRegistry)
        try:
            urlregistry = registry.forInterface(IMultimediaAdminJS)
        except KeyError:
            urlregistry = None
        js_url = ""
        if urlregistry and urlregistry.url and urlregistry.secret and urlregistry.path:
            js_url = urlregistry.url
            secret = urlregistry.secret
            path = urlregistry.path
            user = self.context.portal_membership.getAuthenticatedMember().getUserName()
            expire = (datetime.now() + timedelta(seconds=60)).strftime("%s")
            st = hashlib.md5('%s%s%s' % (secret, path, expire)).hexdigest()
            user_key = hashlib.md5('%s%s' % (user, secret)).hexdigest()
            js_url += '?st=%s&e=%s&user=%s&user_key=%s' % (st, expire, user, user_key)
        return js_url
