# -*- coding: utf-8 -*-
# Zope imports
from zope.interface import Interface
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from five import grok

# Plone imports
from plone.app.portlets.portlets.navigation import Assignment
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder


# Local imports
from Products.CMFCore.utils import getToolByName


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
        self.data = Assignment(root=self.navroot_path)

        tab = aq_inner(self.context)

        strategy = getMultiAdapter((tab, self.data), INavtreeStrategy)
        queryBuilder = DropdownQueryBuilder(tab)
        query = queryBuilder()

        if query['path']['query'] != self.navroot_path:
            self.data = buildFolderTree(tab, obj=tab, query=query,
                                        strategy=strategy)
        else:
            self.data = {}
