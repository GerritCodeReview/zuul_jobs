Run bazelisk build

Runs bazelisk build with the specified targets.

**Role Variables**

.. zuul:rolevar:: bazelisk_targets
   :default: ""

   The bazelisk targets to build.

.. zuul:rolevar:: bazelisk_test_targets
   :default: ""

   The bazelisk targets to test.  ``bazelisk test`` will only be run
   if this value is not the empty string.

.. zuul:rolevar:: bazelisk_executable
   :default: bazelisk

   The path to the bazelisk executable.  See
   :zuul:role:`ensure-bazelisk`.

.. zuul:rolevar:: bazelisk_artifacts
   :default: []

   Paths (relative to zuul_work_dir) of artifacts to collect.

.. zuul:rolevar:: bazelisk_cache
   :default: ""

   Bazelisk arguments relating to cache.  Use this to enable a remote
   or local disk cache.

.. zuul:rolevar:: zuul_output_dir
   :default: {{ ansible_user_dir }}/zuul-output

   Base directory for collecting job output.

.. zuul:rolevar:: zuul_work_dir
   :default: {{ ansible_user_dir }}/{{ zuul.project.src_dir}}

   The working directory in which to run bazelisk.
