# -*- coding: utf-8 -*-
# Zope imports
from zope.interface import Interface
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from five import grok

# Plone imports
from plone.app.layout.viewlets.interfaces import IPortalFooter

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
