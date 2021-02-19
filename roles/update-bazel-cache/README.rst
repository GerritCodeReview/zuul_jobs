Update a remote bazel cache in GCS with the contents of a local cache

**Role Variables**

.. zuul:rolevar:: bazel_cache_server_root
   :default: /opt/bazel-cache

   The root directory with the local cache.

.. zuul:rolevar:: bazel_cache_uri
   :default: /

   The URI of the bazel cache.  Set this to match the remote cache
   URI; this will be appended to the local cache directory.

.. zuul:rolevar:: bazel_cache_credentials_file

   This upload role normally uses Google Cloud Application Default
   Credentials, however it can also operate in a mode where it uses a
   credential file written by gcp-authdaemon:
   https://opendev.org/zuul/gcp-authdaemon

   To use this mode of operation, supply a path to the credentials
   file previously written by gcp-authdaemon.

   Also supply :zuul:rolevar:`update-bazel-cache.zuul_log_project`.

.. zuul:rolevar:: bazel_cache_project

   When using
   :zuul:rolevar:`upload-logs-gcs.zuul_log_credentials_file`, the name
   of the Google Cloud project of the log container must also be
   supplied.
