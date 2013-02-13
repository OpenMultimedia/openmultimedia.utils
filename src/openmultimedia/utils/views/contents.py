import json

from AccessControl import Unauthorized, getSecurityManager

from zope.security import checkPermission
from zope.component import queryUtility, getMultiAdapter
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import Interface

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from five import grok

from plone.uuid.interfaces import IUUID
from plone.app.querystring import queryparser
from plone.app.collection.interfaces import ICollection
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.ATContentTypes.interfaces import IATImage

from plone.principalsource.source import UsersVocabularyFactory

from collective.nitf.vocabulary import AvailableGenresVocabulary
from collective.nitf.vocabulary import SectionsVocabulary

from openmultimedia.contenttypes.content.video import IVideo

from openmultimedia.utils import _

grok.templatedir("templates")

order_by_vocab = SimpleVocabulary(
    [SimpleTerm(value=u'title', title=_(u'Title')),
     SimpleTerm(value=u'creation_date', title=_(u'Creation Date')), ])

MONTHS_DICT = {
    '01': _(u'January'),
    '02': _(u'February'),
    '03': _(u'March'),
    '04': _(u'April'),
    '05': _(u'May'),
    '06': _(u'June'),
    '07': _(u'July'),
    '08': _(u'August'),
    '09': _(u'September'),
    '10': _(u'October'),
    '11': _(u'November'),
    '12': _(u'December'),
}


class MyContentsView(grok.View):
    grok.context(ICollection)
    grok.name("contents_view")
    grok.template("contents_view")
    grok.require("zope2.View")

    def update(self):
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized()
        self.request.set('disable_border', 1)
        self.filters = self.request.get('selected', 'creation_date')
        self.genre = self.request.get('genre', None)
        self.section = self.request.get('section', None)
        self.states = self.request.get('states', None)
        self.search = self.request.get('search', None)
        self.creator = self.request.get('creator', None)
        self.content_type = self.request.get('content-type', None)
        self.order = self.request.get('order', None)
        if self.order == "None":
            self.order = None
        self.order_direction = self.request.get('order-direction', None)
        if self.order_direction == "None":
            self.order_direction = None
        if self.filters:
            self.articles = self.get_contents(self.filters)
        else:
            self.articles = self.get_contents()

    def url(self):
        return self.context.absolute_url() + "/contents_view"

    def is_editor(self):
        return self._checkPermInFolder("cmf.AddPortalContent")

    def get_contents(self, filters=None):
        collectionobj = self.context
        catalog = getToolByName(self.context, 'portal_catalog')
        query = queryparser.parseFormquery(collectionobj,
                                           collectionobj.getRawQuery())
        query['sort_on'] = 'created'
        query['sort_order'] = 'descending'
        if filters == 'title':
            query['sort_on'] = 'sortable_title'
            query['sort_order'] = 'ascending'
        if self.states and self.states != 'all':
            query['review_state'] = self.states
        if self.section and self.section != 'all':
            query['section'] = self.section
        if self.genre and self.genre != 'all':
            query['genre'] = self.genre
        if self.creator and self.creator != 'all' and self.is_editor():
            query['Creator'] = self.creator
        if not self.is_editor():
            user = self.context.portal_membership.getAuthenticatedMember().id
            query['Creator'] = user
        if self.content_type and self.content_type != 'all':
            query['portal_type'] = self.content_type
        if self.search:
            query['SearchableText'] = self.search
        if self.order:
            if self.order == 'date':
                query['sort_on'] = 'Date'
            elif self.order == 'title':
                query['sort_on'] = 'sortable_title'
        if self.order_direction:
            if self.order_direction == "up":
                query['sort_order'] = "ascending"
            else:
                query['sort_order'] = "descending"
        result = catalog(query)
        return result

    def get_date(self, obj):
        date = ""
        if hasattr(obj, 'effective') and self.get_state == 'published':
            date = obj.effective()
        elif hasattr(obj, 'created'):
            date = obj.created()
        return self.format_date(date)

    def format_date(self, date):
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        hour = date.strftime("%H")
        minutes = date.strftime("%M")
        return "%s/%s/%s, %s:%s" % (day, month, year, hour, minutes)

    def get_section(self, obj):
        section = ""
        if hasattr(obj, 'section'):
            section = obj.section
        return section

    def get_icon(self, obj):
        url = obj.getIconURL()
        return url

    def get_normalized_contettype(self, obj):
        idnormalizer = queryUtility(IIDNormalizer)
        portal_types = getToolByName(self.context, "portal_types")
        result = getattr(obj, 'portal_type', 'default')
        if result in portal_types.keys():
            return portal_types[result].title
        return idnormalizer.normalize(result)

    def get_state(self, obj):
        return self.currentStateTitle(obj)

    def _get_brains(self, obj, object_provides=None):
        """ Return a list of brains inside the NITF object.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(obj.getPhysicalPath())
        brains = catalog(object_provides=object_provides, path=path,
                         sort_on='getObjPositionInParent')

        return brains

    def get_images(self, obj):
        """ Return a list of image brains inside the NITF object.
        """
        return self._get_brains(obj, IATImage.__identifier__)

    def get_videos(self, obj):
        """ Return a list of image brains inside the NITF object.
        """
        return self._get_brains(obj, IVideo.__identifier__)

    def has_images(self, obj):
        """ Return the number of images inside the NITF object.
        """
        return len(self.get_images(obj))

    def has_videos(self, obj):
        """ Return the number of images inside the NITF object.
        """
        return len(self.get_videos(obj))

    def getImage(self, obj):
        images = self.get_images(obj)
        if len(images) > 0:
            return images[0].getObject()
        return None

    def getVideo(self, obj):
        videos = self.get_videos(obj)
        if len(videos) > 0:
            return videos[0].getObject()
        return None

    def imageCaption(self, obj):
        image = self.getImage(obj)
        if image is not None:
            return image.Description()

    def tag(self, obj, **kwargs):
        # tag original implementation returns object title in both, alt and
        # title attributes
        image = self.getImage(obj)
        if image is not None:
            return image.tag(**kwargs)

    def get_title(self, obj):
        title = obj.Title()
        if len(title) > 63:
            title = title[:60] + "..."
        return title

    def get_media(self, obj):
        """ Return a list of object brains inside the NITF object.
        """
        media_types = ['Image', 'Video']

        return self._get_brains(obj, media_types)

    def get_batch(self):
        #cannot put it on top of file grok error :S
        from Products.CMFPlone import Batch
        return Batch

    def get_order_vocab(self):
        return order_by_vocab

    def currentStateTitle(self, obj):
        context_state = getMultiAdapter((obj, self.request), name='plone_context_state')
        tools = getMultiAdapter((obj, self.request), name='plone_tools')
        state = context_state.workflow_state()
        workflows = tools.workflow().getWorkflowsFor(obj)
        if workflows and state:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state
        return ""

    def currentState(self, obj):
        context_state = getMultiAdapter((obj, self.request), name='plone_context_state')
        state = context_state.workflow_state()
        result = ""
        if state:
            result = state
        return result

    def can_modify_object(self, obj):
        return getSecurityManager().checkPermission(
            permissions.ModifyPortalContent, obj)

    def get_uid(self, obj):
        return IUUID(obj, None)

    def get_sections(self):
        return SectionsVocabulary()(self.context)

    def get_genres(self):
        return AvailableGenresVocabulary()(self.context)

    def get_states(self):
        collectionobj = self.context
        states = {}
        wt = self.context.portal_workflow
        query = queryparser.parseFormquery(collectionobj,
                                           collectionobj.getRawQuery())
        if 'portal_type' in query.keys() and 'query' in query['portal_type'].keys():
            for ct in query['portal_type']['query']:
                wkfs = wt.getChainForPortalType(ct)
                if wkfs:
                    wkf_states_obj = wt.getWorkflowById(wkfs[0]).states
                    for state in wkf_states_obj.keys():
                        states[state] = wkf_states_obj[state].title or state
        return states

    def get_contettypes(self):
        collectionobj = self.context
        contents = {}
        portal_types = getToolByName(self.context, "portal_types")
        query = queryparser.parseFormquery(collectionobj,
                                           collectionobj.getRawQuery())
        if 'portal_type' in query.keys() and 'query' in query['portal_type'].keys():
            for ct in query['portal_type']['query']:
                ct_name = ct
                if ct in portal_types.keys():
                    ct_name = portal_types[ct].title
                contents[ct] = ct_name
        return contents

    def get_fullname(self, user_id):
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getMemberById(user_id)
        if member.hasProperty('fullname'):
            fullname = member.getProperty('fullname')
            if fullname:
                return fullname
        return user_id

    def get_user_list(self):
        source = UsersVocabularyFactory(self.context)
        return source

    def _checkPermInFolder(self, perm, folder_id=None):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if folder_id:
            try:
                folder = portal[folder_id]
            except KeyError:
                folder = None
        else:
            folder = portal
        if folder:
            can_add = checkPermission(perm, folder)
        else:
            can_add = False

        return can_add


class DeleteButton(grok.View):
    grok.context(Interface)
    grok.name("delete-object")
    grok.require("zope2.View")

    def __call__(self, delete_id=None):
        parent = self.context.aq_inner.aq_parent

        status = {'status': 'error'}
        if delete_id:
            parent.manage_delObjects([delete_id])
            parent.reindexObject()
            status['status'] = 'success'

        return json.dumps(status)

    def render(self):
        pass
