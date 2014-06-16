====
Reek
====

Reek is a collection of code experiments for content management.

Modules
=======

Reek is composed of four modules. They are independent up to a point,
since the admin interfaces in every module use the `admin` module,
`admin` uses class-based URLs and `restructuredfield` will provide
hooks into the `modelstate` diff-utils.


urlconf
-------

URLconf adds two new mechanisms for generating Django URLs. First it adds
a dynamic mechanism for creating them from the admin. This is awfully
similar to the Page-tree of many CMS'es.

Second, it provides a base class for class-based urls. This feature is
often known as a ViewSet, but in essense it is a way to define urls on a
class and provide some hooks for customisation.

.. toctree::
    :maxdepth: 2

    urlconf/index

admin
-----

A reimagining of the Django admin using Django's class-based views and the
class-based urls provided by `urlconf`. The goal is to have an admin
which can be customised at (m)any point(s).

It removes the dependency of having a Django model as the base for an
admin and an app for a section. It does, of course, provide AppSections
and ModelAdmins for Django apps and models.

.. toctree::
    :maxdepth: 2

    admin/index

modelstate
----------

Content Management Systems need some level of workflow. The simplest
version of this is a draft/live version of an element of your site.
Versioning and workflow actually is hard and requires you to think about
exactly what information you want to version and what the purpose is of a
version. Do you want a complete history or just a mechanism to ensure
information quality? No code yet, since this is an open discussion for the
forseeable future.

restructuredfield
-----------------

Often some part of a site has a region in a template which purpose is
"content". Often we give them a TextField which takes some rendered HTML
from a WYSIWYG-editor and we hack on the editor to allow for the custom
content designed to go in there. reStructuredField is an idea to let the
base of the content be a reST document which will render to HTML and an
editor which translates the reST-structure into editable blocks.
Plugins function as docutils Directives with an HTML output and JavaScript
modules for the editor which outputs the reST.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

