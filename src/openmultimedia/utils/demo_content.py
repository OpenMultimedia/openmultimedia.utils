# -*- coding: utf-8 -*-

# ideas and code on how to populate a site with demo content were shamelessly
# taken from http://www.zopyx.com/blog/generating-demo-content-with-plone

import logging
import loremipsum
import random
import urllib2

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName

from plone.i18n.normalizer import idnormalizer

from laradiodelsur.web.policy.config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)


def generate_sentence():
    return loremipsum.Generator().generate_sentence()[-1]


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
    factory = getUtility(IVocabularyFactory, 'collective.nitf.AvailableGenres')
    v = [t.value for t in factory(context)]
    i = random.randint(0, len(v) - 1)
    return v[i]


def random_section(context):
    """ Returns a random value from the AvailableSections vocabulary.
    """
    factory = getUtility(IVocabularyFactory, 'collective.nitf.AvailableSections')
    v = [t.value for t in factory(context)]
    i = random.randint(0, len(v) - 1)
    return v[i]


def generate_articles(context, num=4):
    """ Creates a News Article with a number of images on it. The News Article
    will have a title; a subtitle; a resume (made of 3 sentences); a
    byline; a body text (made of 5 paragraphs); it will be classified with
    a random genre and section; and it will contain 4 random images.
    """
    title = generate_sentence()
    oid = idnormalizer.normalize(title, 'es')
    context.invokeFactory('collective.nitf.content', id=oid, title=title)
    article = context[oid]
    article.description = generate_sentences(3)
    article.subtitle = generate_sentence()
    article.byline = generate_sentence()
    article.text = generate_text()
    article.genre = random_genre(context)
    article.section = random_section(context)
    article.location = generate_sentence()

    logger.debug("News Article '%s' created" % title)

    for i in range(num):
        title = generate_sentence()
        oid = idnormalizer.normalize(title, 'es')
        description = generate_sentences(2)
        image = generate_image(1024, 1024)
        article.invokeFactory('Image', id=oid, title=title,
                              description=description, image=image)

    logger.debug("%s images created" % num)

    article.reindexObject()

    workflowTool = getToolByName(context, 'portal_workflow')
    workflowTool.doActionFor(article, 'publish')

    logger.debug("News Article reindexed and published")


def generate_polls(context, num=5):
    pass


def generate_galeries(context, num=10):
    """ Creates a News Article with a number of images on it. The News Article
    will have a title; a subtitle; a resume (made of 3 sentences); a
    byline; a body text (made of 5 paragraphs); it will be classified with
    a random genre and section; and it will contain 4 random images.
    """
    title = generate_sentence()
    oid = idnormalizer.normalize(title, 'es')
    context.invokeFactory('openmultimedia.contenttypes.gallery', id=oid,
                          title=title)
    gallery = context[oid]
    gallery.description = generate_sentences(3)
    gallery.text = generate_text(1)
    gallery.section = random_section(context)

    logger.debug("Gallery '%s' created" % title)

    for i in range(num):
        title = generate_sentence()
        oid = idnormalizer.normalize(title, 'es')
        description = generate_sentences(2)
        image = generate_image(1024, 1024)
        gallery.invokeFactory('Image', id=oid, title=title,
                              description=description, image=image)

    logger.debug("%s images created" % num)

    gallery.reindexObject()

    workflowTool = getToolByName(context, 'portal_workflow')
    workflowTool.doActionFor(gallery, 'publish')

    logger.debug("Gallery reindexed and published")


def generate(context):
    if context.readDataFile('laradiodelsur.web.policy-demo.txt') is None:
        return

    portal = context.getSite()
    folder = portal['articulos']
    for i in range(20):
        generate_articles(folder)
    logger.info("A batch of 20 articles, with 4 images inside each one, was"
                "generated and published")

    for i in range(5):
        generate_galeries(folder)
    logger.info("A batch of 5 galleries, with 10 images inside each one, was"
                "generated and published")
