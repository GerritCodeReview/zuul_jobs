#!/usr/bin/env python3
#
# Copyright 2014 Rackspace Australia
# Copyright 2018-2019 Red Hat, Inc
# Copyright 2021 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


"""
Utility to upload files to google

Run this from the CLI from the zuul/jobs/roles directory with:

  python -m update-bazel-cache.library.gcs_upload
"""

import argparse
import datetime
import json
import logging
import os
try:
    import queue as queuelib
except ImportError:
    import Queue as queuelib
import sys
import threading

from google.cloud import storage
import google.auth.compute_engine.credentials as gce_cred

from ansible.module_utils.basic import AnsibleModule

def retry_function(func):
    for attempt in range(1, POST_ATTEMPTS + 1):
        try:
            return func()
        except Exception:
            if attempt >= POST_ATTEMPTS:
                raise
            else:
                logging.exception("Error on attempt %d" % attempt)
                time.sleep(attempt * 10)

MAX_UPLOAD_THREADS = 24


class Credentials(gce_cred.Credentials):
    def _set_path(self, path):
        """Call this after initialization"""
        self._path = path
        self.refresh(None)

    def refresh(self, request):
        with open(self._path) as f:
            data = json.loads(f.read())
        self.token = data['access_token']
        self.expiry = (datetime.datetime.utcnow() +
                       datetime.timedelta(seconds=data['expires_in']))

    def with_scopes(self, *args, **kw):
        ret = super(Credentials, self).with_scopes(*args, **kw)
        ret._set_path(self._path)
        return ret


class Uploader():
    def __init__(self, client, container):
        self.client = client
        self.bucket = client.bucket(container)

    def upload(self, file_list):
        """Spin up thread pool to upload to storage"""
        num_threads = min(len(file_list), MAX_UPLOAD_THREADS)
        threads = []
        queue = queuelib.Queue()
        # add items to queue
        for f in file_list:
            queue.put(f)

        for x in range(num_threads):
            t = threading.Thread(target=self.post_thread, args=(queue,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    def post_thread(self, queue):
        while True:
            try:
                file_detail = queue.get_nowait()
                logging.debug("%s: processing job %s",
                              threading.current_thread(),
                              file_detail)
                retry_function(lambda: self._post_file(file_detail))
            except IOError:
                # Do our best to attempt to upload all the files
                logging.exception("Error opening file")
                continue
            except queuelib.Empty:
                # No more work to do
                return

    def _post_file(self, file_detail):
        relative_path = file_detail.relative_path

        data = open(file_detail.full_path, 'rb')
        blob = self.bucket.blob(relative_path)
        blob.upload_from_file(data)


def run(container, root, credentials_file=None, project=None):
    if credentials_file:
        cred = Credentials()
        cred._set_path(credentials_file)
        client = storage.Client(credentials=cred, project=project)
    else:
        client = storage.Client()

    file_list = []
    for path, folders, files in os.walk(root):
        for filename in files:
            file_list.append(os.path.join(path, filename))

    uploader = Uploader(client, container)
    uploader.upload(file_list)
    return file_list


def ansible_main():
    module = AnsibleModule(
        argument_spec=dict(
            container=dict(required=True, type='str'),
            root=dict(required=True, type='str'),
            credentials_file=dict(type='str'),
            project=dict(type='str'),
        )
    )

    p = module.params
    file_list = run(p.get('container'), p.get('root'),
                    credentials_file=p.get('credentials_file'),
                    project=p.get('project'))
    module.exit_json(changed=True, file_list=file_list)


def cli_main():
    parser = argparse.ArgumentParser(
        description="Upload files to Google Cloud Storage"
    )
    parser.add_argument('--verbose', action='store_true',
                        help='show debug information')
    parser.add_argument('--credentials-file',
                        help='A file with Google Cloud credentials')
    parser.add_argument('--project',
                        help='Name of the Google Cloud project (required for '
                             'credential file)')
    parser.add_argument('container',
                        help='Name of the container to use when uploading')
    parser.add_argument('root',
                        help='the root of the directory to upload')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.captureWarnings(True)

    append_footer = args.append_footer
    if append_footer.lower() == 'none':
        append_footer = None

    file_list = run(args.container, args.root,
                    credentials_file=args.credentials_file,
                    project=args.project)


if __name__ == '__main__':
    if sys.stdin.isatty():
        cli_main()
    else:
        ansible_main()
