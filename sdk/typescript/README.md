# Cloudspace TypeScript SDK

```ts
import { CloudspaceClient } from "@cloudspace/sdk";

const client = new CloudspaceClient("https://platform.example.com", accessToken);
const { principal } = await client.me();
const billing = await client.billingOverview();
```

The SDK uses browser/Node `fetch`, returns typed Cloudspace contract models, and raises `CloudspaceError` for non-success responses. Never put provider credentials in the browser. Use a backend-for-frontend or an OIDC flow appropriate for the application.

Build with `npm run build`; run tests with `npm test` after installing the package’s development dependencies.
