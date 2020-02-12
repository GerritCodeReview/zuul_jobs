Ensure that bazelisk is present.

If bazelisk is already installed, this role does nothing.  Otherwise,
it downloads bazelisk from the GitHub and installs it in the user's
home directory by default.

**Role Variables**

.. zuul:rolevar:: bazelisk_version
   :default: v1.3.0

   Version of Bazelisk to install

.. zuul:rolevar:: bazelisk_arch
   :default: linux-amd64

   Architecture to install.

.. zuul:rolevar:: bazelisk_url
   :default: https://github.com/bazelbuild/bazelisk/releases/download/{{ bazelisk_version }}/bazelisk-{{ bazelisk_arch }}

   The URL from which to download bazelisk.

.. zuul:rolevar:: bazelisk_target
   :default: "{{ ansible_user_dir }}/.local/bin/bazelisk"

   Where to install bazelisk.  If the role downloads bazelisk, it will
   set :zuul:rolevar:`bazelisk_executable` to this value as well.

.. zuul:rolevar:: bazelisk_executable
   :default: bazelisk

   The path to the bazelisk executable.  If this already exists, the
   role will not perform any further actions.
