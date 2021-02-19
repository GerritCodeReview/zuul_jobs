# Copyright 2021 Monty Taylor
# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import configparser
import os
import subprocess
import sys
import textwrap

from ansible.module_utils.basic import AnsibleModule


class Runner:

    output = []

    def run(self, cmd):
        try:
            out = subprocess.check_output(cmd)
            self.output.extend(out.split('\n'))
        except Exception as e:
            self.output.append(str(e))
            raise

    def print(self, msg):
        self.output.append(msg)


def run(gerrit_project_mapping, gerrit_project_name, gerrit_root, zuul):
    runner = Runner()

    output = []
    # In case there is no matching branch we may need to check out the
    # actual sha defined in the parent repo. The default zuul remote,
    # file:///dev/null, doesn't work here because relative paths cause
    # it to be file:///dev/plugins/download-commands, which isn't a
    # thing. Removing the origin causes git to use relative local
    # filesystem paths.
    os.chdir(gerrit_root)
    runner.run('git remote rm origin')

    for project in zuul['projects'].values():
        project_dest = gerrit_project_mapping.get(
            project['name'],
            project['name'],
        )
        if not project_dest:
            continue

        # Prepare Project
        runner.print("{name} {dest}".format(
            name=project['name'],
            dest=project_dest,
        ))

        # If zuul checked out the branch we're testing (ie, gerrit's
        # branch), then it exists.
        project_branch_exists = (
            zuul['projects'][gerrit_project_name]['checkout']
            == project['checkout']
        )

        # Check if repo has a dependent change
        repo_has_dependent_change = False
        for item in zuul['items']:
            if item['project']['canonical_name'] == project['canonical_name']:
                repo_has_dependent_change = True

        # Check if repo is in submodules
        config = None
        project_in_gitmodules = False
        tracking_branch = False
        try:
            config = configparser.ConfigParser()
            config.read(os.path.join(
                zuul['executor']['work_root'],
                zuul['projects'][gerrit_project_name]['src_dir'],
                '.gitmodules',
            ))
            section_name = "submodule {project_dest}".format(
                project_dest=project_dest,
            )
        except Exception as e:
            runner.print(str(e))
        if config:
            try:
                project_in_gitmodules = config[section_name]['path']
                runner.print(
                    "Project Submodule: {sub}".format(sub=project_in_gitmodules))
            except Exception as e:
                runner.print(str(e))
            try:
                tracking_branch = config[section_name]['branch']
                runner.print(
                    "Tracking Branch: {sub}".format(sub=project_in_gitmodules))
            except Exception as e:
                runner.print(str(e))

        # Check for unsatisfiable source repo condition
        if (
            project['canonical_name'] != zuul['project']['canonical_name']
            and (not project_branch_exists or not tracking_branch)
            and repo_has_dependent_change
        ):

            message = textwrap.dedent("""
                The repository { project_name } does not contain the branch
                under test ({ checkout }),
                but this change depends on a change to that project and branch.
                While Zuul is able to check out the repos in the requested
                state, the branch mismatch means that Gerrit's submodule
                subscription would not automatically update the submodule
                pointer, and the merged state would not reflect the tested
                state.
    
                This configuration would be testable by creating a { checkout }
                branch in the { project_name } repo.  Alternatively, you can merge the
                dependent change, manually update the submodule pointer, then
                test this change again.""".format(
                    project_name=project['name'],
                    checkout=zuul['projects'][gerrit_project_name]['checkout'],
            ))
            raise Exception(message)

        # If there is no matching branch we need to check out the actual sha
        # defined in the parent repo.
        if (
            project_in_gitmodules
            and (not project_branch_exists or not tracking_branch
        ):
            runner.run("git submodule update --init {project_dest}".format(
                project_dest=project_dest))
          
        else:
            runner.run(os.expanduser(
                "mv -T -f ~/{ project_src_dir } { gerrit_root }/{ project_dest }".format(
                project_src_dir=project['src_dir'],
                gerrit_root=gerrit_root,
                project_dest=project_dest,
            )))

    return runner.output
    


def ansible_main():
    module = AnsibleModule(
        argument_spec=dict(
            gerrit_project_mapping=dict(required=True, type='raw'),
            gerrit_project_name=dict(required=True, type='str'),
            gerrit_root=dict(required=True, type='str'),
            zuul_dict=dict(required=True, type='raw'),
        )
    )

    p = module.params
    try:
        debug_out = run(
            gerrit_project_mapping=p.gerrit_project_mapping,
            gerrit_project_name=p.gerrit_project_name,
            gerrit_root=p.gerrit_root,
            zuul=p.zuul_dict,
        )
        module.exit_json(
            changed=True,
            debug_out=debug_out,
        )
    except Exception as e:
        module.fail_json(
            msg=str(e),
        )


def cli_main():
    pass


def ansible_main():
    pass

import sys


if __name__ == '__main__':

    if sys.stdin.isatty():
        cli_main()
    else:
        ansible_main()
