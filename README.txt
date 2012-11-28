********************
openmultimedia.utils
********************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

A collection of helper methods and functions for use among  Open Multimedia
projects.

Don't Panic
-----------

TBA.


Util Links Viewlet
------------------

A viewlet is provided that allows to render links anywhere in your site.
To use it, you need to first register the viewlet into the viewlet manager of your choice, and then to load links.

1. Register the viewlet::

        <browser:viewlet
            name="openmultimedia.utils.link"
            for="*"
            manager="plone.app.layout.viewlets.interfaces.IPortalFooter"
            class="openmultimedia.utils.viewlets.OpenMultimediaUtilLinks"
            permission="zope.Public"
            />

  This is pretty straight forward, you need to add this piece to your configure.zcml
  Make sure you choose the correct manager under the manager attribute.

2. Add links to be shown by the viewlet::

        <registry xmlns:i18n="http://xml.zope.org/namespaces/i18n"
          i18n:domain="openmultimedia.utils">

            <records interface="openmultimedia.utils.viewlets.IUtilLink"
                     prefix="openmultimedia.utils.links.google">
                <value key="text" i18n:translate="">Google</value>
                <value key="uri">http://www.google.com</value>
                <value key="css">absolute css</value>
                <value key="condition"></value>
                <value key="permission"></value>
            </records>
            <records interface="openmultimedia.utils.viewlets.IUtilLink"
                     prefix="openmultimedia.utils.links.portal">
                <value key="text" i18n:translate="">Portal</value>
                <value key="uri">{portal}/articulos/++add++test.content.type</value>
                <value key="css">portal css</value>
                <value key="condition">context.id == 'articles'</value>
                <value key="permission"></value>
            </records>
            <records interface="openmultimedia.utils.viewlets.IUtilLink"
                     prefix="openmultimedia.utils.links.relative">
                <value key="text" i18n:translate="">Relative</value>
                <value key="uri">{relative}/++add++test.nada</value>
                <value key="css">relative css</value>
                <value key="condition"></value>
                <value key="permission">Manage Portal</value>
            </records>

            <record field="links" 
                    interface="openmultimedia.utils.viewlets.IUtilLinks">
              <field type="plone.registry.field.List">
                <title>Links</title>
                <value_type type="plone.registry.field.DottedName"></value_type>
              </field>
              <value>
                <element>openmultimedia.utils.links.google</element>
                <element>openmultimedia.utils.links.portal</element>
                <element>openmultimedia.utils.links.relative</element>
              </value>
            </record>
        </registry>

  The first part, will register 3 links::
    * Google, which is an absolute URL, with no condition nor permission check
    * Portal, which has its first part replaced by the portal root URL, and will only be shown when the context id is 'articles'
    * Relative, which has its first part replaced by the current context URL, and will only be shown for members with the "Manage Portal" permission.

  The second part, actually tells the viewlet which links to render. As you can see, the elements name, should match the "prefix" part of the links defined on top. These prefixes can be anything, but they should match in both places, and they should be unique.


Additional notes
++++++++++++++++

  * The "uri" parameter, accepts {portal}/ and {relative}/ at the beginning and it will replace it with the portal and current context url repspectively.
  * The "css" parameter, lets you add additional css classes to be used in case you need it.
  * The "condition" paramter, evaluates a python expression. In it, you can use "context", "request", "portal", "auth_member" and "is_anon".
  * The "permission" parameter, will evaluate if the currently logged in user has that permission for the current context object.
  * Please note, that the interface for the list of links is IUtilLinks and the one for each link is IUtilLink.


Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/openmultimedia/openmultimedia.utils.png
    :target: http://travis-ci.org/openmultimedia/openmultimedia.utils

Have an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/openmultimedia/openmultimedia.utils/issues
