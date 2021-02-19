import os
import sys

from ansible.module_utils.basic import AnsibleModule


def run(gerrit_project_mapping, gerrit_project_name, gerrit_root, zuul):
    # In case there is no matching branch we may need to check out the
    # actual sha defined in the parent repo. The default zuul remote,
    # file:///dev/null, doesn't work here because relative paths cause
    # it to be file:///dev/plugins/download-commands, which isn't a
    # thing. Removing the origin causes git to use relative local
    # filesystem paths.
    os.chdir(gerrit_root)
    os.system('git remote rm origin')

    for project in zuul['projects'].values():
        project_dest = gerrit_project_mapping.get(
            project['name'],
            project['name'],
        )
        if not project_dest:
            continue
        process_repo(project, zuul)


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
    run(
        gerrit_project_mapping=p.gerrit_project_mapping,
        gerrit_project_name=p.gerrit_project_name,
        gerrit_root=p.gerrit_root,
        zuul=p.zuul_dict,
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
