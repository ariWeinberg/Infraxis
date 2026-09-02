# Cloudspace documentation index

This documentation describes the intended production architecture and the currently implemented offline vertical slice. Statements marked **implemented** are backed by repository code and tests. Statements marked **target** describe the next production increment and must not be mistaken for deployed capability.

## Start here

1. [Architecture overview](architecture/overview.md)
2. [Contract guide](contracts/guide.md)
3. [Authentication](authentication/oidc.md)
4. [Authorization](authorization/model.md)
5. [Billing](billing/model.md)
6. [Local development](development/local.md)
7. [Deployment](deployment/kubernetes.md)
8. [Operations runbook](operations/runbook.md)
9. [Security model](security/model.md)
10. [Testing strategy](testing/strategy.md)

## Document conventions

- **MUST** is a requirement for a conforming implementation.
- **SHOULD** is the default unless a documented exception exists.
- **MAY** is optional.
- Provider names describe adapters, not consumer-facing contracts.
- Cloudspace is not IAM. It does not manage arbitrary users, groups, roles, access keys, or permissions for unrelated products.
