from __future__ import annotations

import hashlib
import logging

import diskcache
from httpx import ByteStream, HTTPTransport, Request, Response

log = logging.getLogger(__name__)


class CachingHTTPTransport(HTTPTransport):
    def __init__(self, cache: diskcache.Cache, **kwargs) -> None:
        self.cache = cache
        super().__init__(**kwargs)

    def handle_request(self, request: Request) -> Response:
        key = self.get_request_cache_key(request)
        if key:
            response = self.cache.get(key)
            if response:
                log.info(f"Got cached response for {request.method} {request.url}")
                return response
        resp = super().handle_request(request)
        if key:
            resp.read()
            self.cache.set(key, resp, expire=60 * 60 * 4)
        return resp

    def get_request_cache_key(self, request: Request) -> str | None:
        if not isinstance(request.stream, ByteStream):  # ah, nope
            return None
        body_hash = hashlib.sha256(request.stream._stream).hexdigest()
        key = "\t".join(
            [
                request.method,
                str(request.url),
                body_hash,
                "\t".join(
                    f"{k}={v}"
                    for k, v in sorted(request.headers.items())
                    if k.lower() != "cookie"
                ),
            ]
        )
        return key
