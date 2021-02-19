Run a tiered bazel cache server

This starts an Nginx server that proxies to a remote bazel cache but
also accepts PUT requests for a local cache.

Note: it does not currently serve requests from the local cache.

**Role Variables**

.. zuul:rolevar:: bazel_cache_server_root
   :default: /opt/bazel-cache

   The root directory to hold the cache.

.. zuul:rolevar:: bazel_cache_container
   :required:

   The container of the remote bazel cache.  This will be appended to
   the local cache directory.

.. zuul:rolevar:: bazel_cache_remote_url
   :default: https://storage.googleapis.com

   The protocol and hostname for the remote cache.  Omit the URI and
   set ``bazel_cache_container``.
