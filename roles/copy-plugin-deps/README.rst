Copy plugin bazel deps

If the plugin being built has an ``external_plugin_deps.bzl`` file,
copy it into the Gerrit plugins directory.

**Role Variables**

.. zuul:rolevar:: gerrit_plugin
   :default: zuul.project.short_name

   The name of the plugin to be built.
