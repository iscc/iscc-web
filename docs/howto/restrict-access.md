---
icon: lucide/lock
description: Run a permissioned iscc-web instance behind an authenticating reverse proxy - basic auth or single sign-on, and what private files mean then.
---

# Restrict access

`iscc-web` has no user accounts, API keys or login of its own: anyone who can reach an instance can
generate ISCC-CODEs, decode codes and create simprints. To run a permissioned instance, put an
authenticating reverse proxy in front of it. The service needs no changes for this - the proxy
decides who gets through, and `iscc-web` serves whoever it lets in.

This builds on the reverse proxy from [Deployment](deployment.md); any reverse proxy or load
balancer with authentication support works.

## What to protect

Protect the whole site. The demo page calls the REST API from the visitor's browser, so one sign-in
in front of everything covers the page, the API and the API docs at `/docs`. Protecting only
`/api/*` keeps the demo page and `/docs` public but still requires the sign-in for every ISCC
request, including the demo page's own.

Leave `/health` unprotected if an external monitor polls it through the proxy. The Docker
`HEALTHCHECK` probes the container directly and is not affected by the proxy.

## Basic authentication

The quickest option for a small, fixed group of users: most reverse proxies support HTTP basic
authentication out of the box. Store only password hashes in the proxy configuration, and exempt
`/health` if an external monitor polls it.

Browsers ask for the credentials once and send them with every request, including the demo page's
API calls. Scripts pass them with each request, for example `curl -u alice:<password> ...`.

## Single sign-on

To sign users in with an existing identity provider (Microsoft Entra ID, Google Workspace, GitHub,
Keycloak or any other OpenID Connect provider), use an authentication proxy: an identity-aware
proxy offered by your cloud or platform provider, or an open-source one such as
[oauth2-proxy](https://oauth2-proxy.github.io/oauth2-proxy/). It either sits in front of
`iscc-web` itself or is consulted by your reverse proxy for every request (often called forward
authentication or auth request). Requests from users who are not signed in are redirected to the
identity provider's sign-in page; again, exempt `/health` for external monitors.

For scripts, let the authentication proxy also accept bearer tokens issued by the same identity
provider (oauth2-proxy: `--skip-jwt-bearer-tokens`), so automated clients do not need a browser
sign-in.

## Private files behind a login

With `ISCC_WEB_PRIVATE_FILES=true` (the default), only the uploader of a file may download it,
delete it or embed metadata into it (see [Private files](configuration.md#private-files)). The
service recognises the uploader by a hash of the client IP address, not by the signed-in user:

- Users who share an IP address - an office behind one internet connection, a VPN - count as one
    uploader and can download, delete or embed into each other's uploads.
- A user whose IP address changes loses access to their own earlier uploads. Uploads are deleted
    after `ISCC_WEB_STORAGE_EXPIRY` seconds anyway.

The ISCC results themselves are returned in the response to each request and are not affected.
Keep forwarding the real client IPs as described in
[Forwarded client IPs](deployment.md#forwarded-client-ips); otherwise all signed-in users share the
proxy's IP and therefore one identity.

## Rate limiting

A login controls who may use the instance, not how much. To cap the request rate per user or per IP
address, add rate limiting at the proxy; most reverse proxies and load balancers support it.
Processing is CPU-bound and runs in a fixed pool of worker processes (see [Resource sizing](deployment.md#resource-sizing)), so limits
protect the service from being saturated by a single client.

## Hostname and path

`iscc-web` must be served at the root of a domain or subdomain, such as `https://iscc.example.com/`.
The demo page, the API docs and the URLs in API responses use root paths (`/api/v1`, `/static`,
`/docs`), so serving the service under a path of a shared hostname, such as
`https://intranet.example.com/iscc/`, is not supported.

## Several instances

Running more than one `iscc-web` instance behind the proxy requires session affinity
("sticky sessions"); see [Several instances](deployment.md#several-instances).
