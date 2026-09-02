# SDK reference

## Design goals

The Python and TypeScript SDKs are thin contract clients. They provide consistent base URL handling, bearer authentication, typed responses, and structured errors. They do not reimplement authorization, cache billing state, or expose provider APIs.

## Python

Package: `sdk/python`, import namespace: `cloudspace_sdk`.

Available clients:

- `CloudspaceClient` for synchronous applications;
- `AsyncCloudspaceClient` for asynchronous applications.

Available operations:

- `me()` -> normalized `Principal`;
- `authorize(AuthorizationCheckRequest)` -> `AuthorizationDecision`;
- `billing_overview()` -> `BillingOverview`.

Always close the client. Set a bounded transport timeout in the hosting application and propagate request/trace headers when the application participates in a distributed trace.

## TypeScript

Package: `sdk/typescript`, package name: `@cloudspace/sdk`.

The `CloudspaceClient` exposes `me()`, `authorize()`, and `billingOverview()`. Models intentionally use the exact snake_case wire names from the canonical API. `CloudspaceError.requestId` should be included in support tickets and logs; do not log access tokens.

## Versioning

SDK major/minor releases follow the API compatibility policy. A client may add support for new optional response properties without a release, but breaking wire changes require a new API version and a coordinated SDK release. Generated clients should eventually replace hand-maintained model declarations while preserving these package-level ergonomics.
