Prepare gerrit submodules

Gerrit has a number of repos which are submodules of the Gerrit repo,
and some plugins are expected to be built by being copied into the
Gerrit repo.  This is generally compatible with the way Zuul operates,
but special care needs to be taken.

Zuul prepares the git repository states for all of the projects
involved in testing a change.  These projects may include the project
that the change is against, any other project if the change has a
"Depends-On" footer pointing to a change in that other project, and
any projects which the job specifies with "required-projects".  These
git repository states represent the proposed future state of the
world, in all branches, with dependent changes applied.

This matches well with Gerrit's submodule subscription system, in that
if a change to Gerrit "Depends-On" a change to a plugin, then as soon
as that plugin change merges, The submodule in the Gerrit repo will be
updated to the new plugin sha.  In other words, we can say with high
confidence that the state of the world that was tested in Zuul is what
actually resulted after the merge.

However, Zuul itself does not perform any actions on submodules.  A
simple "git submodule update --init" would discard the state of the
repositories that Zuul prepared and would invalidate our testing.  But
since Zuul has already prepared the repos, we don't need to use a "git
submodule" command, we just need to move them into the correct
location.  That is what this role does.

There is one edge case: if a repo does not have the branch that is
being tested, then Gerrit's submodule subscription does not work.
That means that Zuul may not have checked out the same git sha as the
submodule pointer in the gerrit repo, and we can not assume that if a
change in a plugin lands, that the submodule pointer will be updated.
In this case, this role falls back to performing a "git submodule
update --init".  If, however, there is a dependent change in that
repo, then this role will fail the job.  That is an untestable
situation that can only be resolved by merging the dependent change
and manually updating the submodule pointer in the Gerrit repo.

The best way to avoid that situation is to ensure that all the
dependent projects have the same branches as Gerrit itself.

**Role Variables**

.. zuul:rolevar:: gerrit_project_mapping
   :type: dict

   A dictionary to map Gerrit sub-projects to their location in the
   gerrit repo.  This role iterates over every Zuul project and
   assumes that it should be copied into the gerrit project with its
   full project name.  For example, the `plugins/download-commands`
   project will be copied into the ``plugins/download-commands``
   directory under gerrit.  To specify an alternate location, add an
   entry to this dictionary in the form ``project_name:
   destination_dir``.  To omit copying the project into the gerrit
   repo, supply the empty string.

   The following is the default value; it instructs the role not to
   copy the gerrit project into itself, and to copy the jgit project
   into ``modules/jgit``:

   .. code-block:: yaml

      gerrit_project_mapping:
        gerrit: ''
        jgit: modules/jgit

.. zuul:rolevar:: gerrit_project_name
   :default: gerrit.googlesource.com/gerrit

   The canonical name of the Gerrit repository.  This role uses this
   value to look up the branch of Gerrit which is checked out in order
   to detect whether or not sub-projects contain the same branch.
