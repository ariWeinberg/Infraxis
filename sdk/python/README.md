# Cloudspace Python SDK

The SDK exposes Cloudspace-owned models and endpoints. It deliberately does not expose Authentik, OPA, OPAL, or Stripe SDK objects.

```python
from cloudspace_sdk import CloudspaceClient

client = CloudspaceClient("https://platform.example.com", access_token)
try:
    principal = client.me()
    overview = client.billing_overview()
finally:
    client.close()
```

Use `AsyncCloudspaceClient` in async services and call `aclose()` during shutdown. `CloudspaceError` contains the stable Cloudspace error code, request ID, HTTP status, and safe message. Authorization responses are decisions; callers must enforce `decision is True` and must not treat timeouts as allows.

Install with `pip install cloudspace-sdk` after publishing the package, or use the local editable package while developing:

```bash
pip install -e sdk/python
```
