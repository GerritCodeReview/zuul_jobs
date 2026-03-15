Copy plugin Bazel dependency files
==================================

This role copies Bazel dependency files from a plugin source tree
into the Gerrit ``plugins`` directory when they are present.

If the plugin being built contains an ``external_plugin_deps.bzl`` file,
it is copied into the Gerrit plugins directory.

If the plugin being built contains an ``external_plugin_deps.MODULE.bazel``
file, it is also copied into the Gerrit plugins directory.

Both files are optional and are copied only if they exist.

**Role Variables**

.. zuul:rolevar:: gerrit_plugin
   :default: zuul.project.short_name

   The name of the plugin to be built.
