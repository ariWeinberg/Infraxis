# Billing and Stripe model

## Domain boundary

Cloudspace owns the meaning of `BillingAccount`, `Plan`, `Subscription`, `Entitlement`, `UsageRecord`, `Invoice`, and `PaymentStatus`. Stripe is a provider adapter. A Stripe Subscription object must never appear in a Cloudspace response.

```json
{
  "id": "sub_123",
  "billing_account_id": "billacct_123",
  "plan_id": "plan_standard",
  "status": "active",
  "provider": {"type": "stripe", "external_id": "sub_1Abc"}
}
```

Cloudspace IDs and provider references are separate fields so Stripe can be replaced or reconciled later.

## State ownership

The platform owns the local billing projection and entitlement projection. Stripe owns payment-provider truth. When the two disagree, reconciliation determines the safe transition; a transient Stripe outage must not erase known local state.

## Webhook processing target

1. Receive the raw body and signature header.
2. Verify the Stripe signature before parsing business data.
3. Persist the provider event ID and raw provider metadata in a durable event table.
4. If the event ID already succeeded, return success without repeating the transition.
5. Apply a validated, monotonic state transition in a database transaction.
6. Write an audit event and entitlement projection/outbox record in the same transaction.
7. Acknowledge only after durable persistence; retry failures safely.

Delivery is at-least-once. The system MUST handle duplicates, delayed events, out-of-order events, retries, replay, and dead-lettered failures. It MUST NOT trust event arrival order as state order.

## Entitlements

Entitlements are derived billing facts, not authorization decisions:

```text
Stripe state -> local subscription state -> entitlement projection -> OPAL data -> OPA decision
```

Authorization uses local entitlement data. It does not synchronously call Stripe. The consistency target is explicitly eventual: a billing change propagates after webhook processing and OPAL synchronization. During uncertainty, protected operations fail closed while known billing state remains available for support and reconciliation.

## Required operations

- inspect webhook event status and failure reason;
- replay a verified event safely;
- reconcile a billing account against Stripe;
- compare local and provider IDs/statuses;
- suspend or restore entitlement projection only through an audited operator action;
- rotate webhook secrets without losing the old-secret overlap window.
