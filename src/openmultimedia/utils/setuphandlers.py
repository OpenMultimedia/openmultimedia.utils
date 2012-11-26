# -*- coding: utf-8 -*-

import logging

from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool \
    import WorkflowPolicyConfig_id

from Products.GenericSetup.upgrade import listUpgradeSteps

from plone.i18n.normalizer import idnormalizer

from openmultimedia.utils.config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)

_PROFILE_ID = 'vtv.web.policy:default'
INITIAL_PROFILE_ID = 'profile-%s:initial' % PROJECTNAME


def import_initial(context):
    """ Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('%s_various.txt' % PROJECTNAME) is None:
        return
    logger = context.getLogger(PROJECTNAME)
    site = context.getSite()
    apply_initial_profile(site, logger)


def apply_initial_profile(context, logger):
    """ Method to apply our initial GS profile, including dependencies.

    To see if a dependency profile has already been installed, we could run
    'portal_setup.getProfileImportDate(profile_id)', but this only gives a
    date for profiles that are directly applied, not as dependencies. Also,
    when someone removes install logs from portal_setup in the ZMI, this date
    will come up empty as well. So instead we apply all recursive dependencies
    ourselves, which is actually quite easy.
    """

    setup = getToolByName(context, 'portal_setup')
    logger.info("Checking if initial profile %s or one of its (recursive) "
                "dependencies need to be applied.", INITIAL_PROFILE_ID)
    for dependency in setup.getProfileDependencyChain(INITIAL_PROFILE_ID):
        # Note: getting the profile dependency chain already fails
        # with a KeyError when our profile id, or one of its
        # (recursive) dependencies does not exist.
        if not setup.getProfileImportDate(dependency):
            logger.info("Applying dependency profile %s.",
                        dependency)
            setup.runAllImportStepsFromProfile(dependency,
                                               ignore_dependencies=True)
        else:
            logger.info("Dependency profile %s already applied.",
                        dependency)


def run_upgrade_steps(context):
    """ Run Upgrade steps
    """
    if context.readDataFile('%s_various.txt' % PROJECTNAME) is None:
        return
    logger = logging.getLogger(PROJECTNAME)
    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    version = setup_tool.getLastVersionForProfile(_PROFILE_ID)
    upgradeSteps = listUpgradeSteps(setup_tool, _PROFILE_ID, version)

    flatten_steps = []
    for step in upgradeSteps:
        if isinstance(step, list):
            for inner_step in step:
                flatten_steps.append(inner_step)
        else:
            flatten_steps.append(step)

    for step in flatten_steps:
        oStep = step.get('step')
        if oStep is not None:
            oStep.doStep(setup_tool)
            msg = "Ran upgrade step %s for profile %s" % (oStep.title,
                                                          _PROFILE_ID)
            setup_tool.setLastVersionForProfile(_PROFILE_ID, oStep.dest)
            logger.info(msg)


def set_one_state_workflow_policy(obj, logger):
    """ Change object's workflow using CMFPlacefulWorkflow.
    """
    product = 'CMFPlacefulWorkflow'
    obj.manage_addProduct[product].manage_addWorkflowPolicyConfig()
    pc = getattr(obj, WorkflowPolicyConfig_id)
    pc.setPolicyIn(policy='one-state')
    logger.info('%s changed workflow' % obj.getId())


def create_menu_item(context,
                     title,
                     allowed_types=['Topic'],
                     exclude_from_nav=False):
    """Crea una carpeta en el contexto especificado y modifica su política de
    workflows; por omisión, la carpeta contiene colecciones (Topic) y no
    modifica la política de workflow del contenido creado dentro de ella.
    """
    oid = idnormalizer.normalize(title, 'es')
    if not hasattr(context.aq_explicit, oid):  # XXX: avoid acquisition
        context.invokeFactory('Folder', id=oid, title=title)
        folder = context[oid]
        folder.setConstrainTypesMode(constraintypes.ENABLED)
        folder.setLocallyAllowedTypes(allowed_types)
        folder.setImmediatelyAddableTypes(allowed_types)
        set_one_state_workflow_policy(folder, logger)
        if exclude_from_nav:
            folder.setExcludeFromNav(True)
        folder.reindexObject()
    else:
        folder = context[oid]
        folder.setLocallyAllowedTypes(allowed_types)
        folder.setImmediatelyAddableTypes(allowed_types)
        folder.reindexObject()


def create_section(folder,
                   title,
                   genre='Current',
                   section=None):
    """ Crea una colección de Artículos de noticias publicados, que pertenecen
    al género y a la sección especificados; los ordena de forma descendente
    por fecha de publicación, y les asigna una vista por defecto.
    """
    workflowTool = getToolByName(folder, 'portal_workflow')
    oid = idnormalizer.normalize(title, 'es')
    if not hasattr(folder.aq_explicit, oid):
        folder.invokeFactory('Collection', id=oid, title=title)
        collection = folder[oid]

        query = []
        # tipo de contenido
        query.append({'i': 'portal_type',
                      'o': 'plone.app.querystring.operation.selection.is',
                      'v': ['collective.nitf.content']})

        # género
        query.append({'i': 'genre',
                      'o': 'plone.app.querystring.operation.selection.is',
                      'v': [genre]})

        # sección
        if section is not None:
            query.append({'i': 'section',
                          'o': 'plone.app.querystring.operation.selection.is',
                          'v': [section]})

        # estado
        query.append({'i': 'review_state',
                      'o': 'plone.app.querystring.operation.selection.is',
                      'v': ['published']})

        # orden
        sort_on = u'effective'

        # vista por defecto
        default_view = 'section_view'

        collection.query = query
        collection.sort_on = sort_on
        collection.setLayout(default_view)

        # Publicamos
        workflowTool.doActionFor(collection, 'publish')

        # reindexamos para que el catálogo se entere de los cambios
        collection.reindexObject()

    if hasattr(folder.aq_explicit, oid):  # XXX: avoid acquisition
        collection = folder[oid]
        default_view = 'section_view'
        collection.setLayout(default_view)
        collection.reindexObject()


def create_default_section_link(context,
                                remoteUrl=''):
    """ Crea un link apuntando a la vista por defecto en una carpeta.
    """
    if not hasattr(context, 'default'):
        context.invokeFactory('Link', id='default',
                             title=u'Página por defecto',
                             remoteUrl=remoteUrl, excludeFromNav=True)
        context.setLayout('default')
        logger.info('Default view for %s was created' % context.Title())
