Upload files to GCS

    container: "{{ gcs_upload_container }}"
    credentials_file: "{{ gcs_upload_credentials_file }}"
    project: "{{ gcs_upload_project }}"
    root: "{{ gcs_upload_root }}"
    prefix: "{{ gcs_upload_prefix }}"

**Role Variables**

.. zuul:rolevar:: gcs_upload_container

   The name of the container to upload to.

.. zuul:rolevar:: gcs_upload_credentials_file
   :default: /authdaemon/token

   The token file to use for authentication.

.. zuul:rolevar:: gcs_upload_project

   The project name to use with the auth token.

.. zuul:rolevar:: gcs_upload_prefix
   :default: ''

   A path prefix to add before each file.

.. zuul:rolevar:: gcs_upload_root

   The root of the directory to upload.
