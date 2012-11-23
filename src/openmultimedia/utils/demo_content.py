# -*- coding: utf-8 -*-

# ideas and code on how to populate a site with demo content were shamelessly
# taken from http://www.zopyx.com/blog/generating-demo-content-with-plone

import logging
import loremipsum
import random
import string
import urllib2

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName

from plone.i18n.normalizer import idnormalizer

from openmultimedia.utils.config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768


def generate_sentence(replace_dots=False):
    g = loremipsum.Generator()
    if replace_dots:
        return string.replace(g.generate_sentence()[-1], '.', '')
    else:
        return g.generate_sentence()[-1]


def generate_sentences(length=10):
    g = loremipsum.Generator()
    return u' '.join([s[2] for s in g.generate_sentences(length)])


def generate_paragraphs(num=1):
    g = loremipsum.Generator()
    return u' '.join([p[2] for p in g.generate_paragraphs(num)])


def generate_text(num=5):
    g = loremipsum.Generator()
    return u'\n'.join(["<p>%s</p>" % p[2] for p in g.generate_paragraphs(num)])


def generate_image(width, height):
    url = 'http://lorempixel.com/%d/%d/' % (width, height)
    return urllib2.urlopen(url).read()


def random_genre(context):
    """ Returns a random value from the AvailableGenres vocabulary.
    """
    random.seed()
    factory = getUtility(IVocabularyFactory, 'collective.nitf.AvailableGenres')
    v = [t.value for t in factory(context)]
    i = random.randint(0, len(v) - 1)
    return v[i]


def random_section(context):
    """ Returns a random value from the AvailableSections vocabulary.
    """
    random.seed()
    factory = getUtility(IVocabularyFactory, 'collective.nitf.AvailableSections')
    v = [t.value for t in factory(context)]
    i = random.randint(0, len(v) - 1)
    return v[i]


def create_image(context):
    title = generate_sentence(replace_dots=True)
    oid = idnormalizer.normalize(title, 'es')
    description = generate_sentences(2)
    image = generate_image(IMAGE_WIDTH, IMAGE_HEIGHT)
    try:
        context.invokeFactory('Image', id=oid, title=title,
                              description=description, image=image)
    except:
        logger.info("An error occurred while creating the image '%s'" % oid)
        return


def create_article(context):
    """ Create a News Article with a random number of images on it. The News
    Article will have a title; a subtitle; a resume (made of 3 sentences); a
    byline; and body text (made of 5 paragraphs); it will be classified with a
    random genre and section.
    """
    title = generate_sentence(replace_dots=True)
    oid = idnormalizer.normalize(title, 'es')
    try:
        context.invokeFactory('collective.nitf.content', id=oid, title=title)
    except:
        logger.info("An error occurred while creating the object '%s'" % oid)
        return

    article = context[oid]
    article.description = generate_sentences(3)
    article.subtitle = generate_sentence(replace_dots=True)
    article.byline = generate_sentence(replace_dots=True)
    article.text = generate_text()
    article.genre = random_genre(context)
    article.section = random_section(context)
    article.location = generate_sentence(replace_dots=True)

    logger.debug("News Article '%s' created in section '%s' with genre '%s'" %
                 (title, article.section, article.genre))

    random.seed()
    images = random.randint(0, 4)
    for i in range(images):
        create_image(article)

    logger.debug("Images created")

    article.reindexObject()

    workflowTool = getToolByName(context, 'portal_workflow')
    workflowTool.doActionFor(article, 'publish')

    logger.debug("News Article reindexed and published")


def set_options(options):
    """ Modify the options to match the way they are stored in a poll.
    """
    tmp = []
    for (index, option) in enumerate(options):
        data = {}
        data['option_id'] = index
        data['description'] = option
        tmp.append(data)
    return tmp


def create_poll(context):
    """ Create a Poll with 3 options on it; each option is given a random
    number of votes.
    """
    title = generate_sentence(replace_dots=True)
    oid = idnormalizer.normalize(title, 'es')
    try:
        context.invokeFactory('collective.polls.poll', id=oid, title=title)
    except:
        logger.info("An error occurred while creating the object '%s'" % oid)
        return

    poll = context[oid]
    poll.description = generate_sentences(3)
    options = [generate_sentence(replace_dots=True),
               generate_sentence(replace_dots=True),
               generate_sentence(replace_dots=True)]

    poll.options = set_options(options)

    random.seed()
    votes = random.sample(xrange(10000), 3)

    poll.annotations['option.00'], \
    poll.annotations['option.01'], \
    poll.annotations['option.02'] = votes

    logger.debug("Poll '%s' created" % title)

    poll.reindexObject()

    workflowTool = getToolByName(context, 'portal_workflow')
    workflowTool.doActionFor(poll, 'open')
    workflowTool.doActionFor(poll, 'close')

    logger.debug("Poll reindexed, published and closed")


def create_gallery(context):
    """ Create a Gallery with a random number of images on it. The Gallery
    will have a title; a resume (made of 3 sentences); and it will be
    classified with a random section.
    """
    title = generate_sentence(replace_dots=True)
    oid = idnormalizer.normalize(title, 'es')
    try:
        context.invokeFactory('openmultimedia.contenttypes.gallery', id=oid,
                              title=title)
    except:
        logger.info("An error occurred while creating the object '%s'" % oid)
        return

    gallery = context[oid]
    gallery.description = generate_sentences(3)
    gallery.text = generate_text(1)
    gallery.section = random_section(context)

    logger.debug("Gallery '%s' created in section '%s'" %
                 (title, gallery.section))

    random.seed()
    images = random.randint(4, 10)
    for i in range(images):
        create_image(gallery)

    logger.debug("Images created")

    gallery.reindexObject()

    workflowTool = getToolByName(context, 'portal_workflow')
    workflowTool.doActionFor(gallery, 'publish')

    logger.debug("Gallery reindexed and published")


def generate(context):
    if context.readDataFile('openmultimedia.utils-demo.txt') is None:
        return

    portal = context.getSite()

    logger.info("Creating a batch of 30 articles")

    for i in range(30):
        create_article(portal['articulos'])

    logger.info("Creating a batch of 5 galleries")
    for i in range(5):
        create_gallery(portal['articulos'])

    logger.info("Creating a batch of 10 polls")
    for i in range(10):
        create_poll(portal['encuestas'])

    logger.info("Demo content successfully created")
