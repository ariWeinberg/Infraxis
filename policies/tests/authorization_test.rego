package cloudspace.authorization

test_same_tenant_billing_read if {
    allow with input as {
        "action": "billing.account.read",
        "principal": {"tenant_id": "tenant-a"},
        "resource": {"tenant_id": "tenant-a"},
        "entitlements": {"billing_read": true}
    }
}

test_cross_tenant_denied if {
    not allow with input as {
        "action": "billing.account.read",
        "principal": {"tenant_id": "tenant-a"},
        "resource": {"tenant_id": "tenant-b"},
        "entitlements": {"billing_read": true}
    }
}

test_missing_entitlement_denied if {
    not allow with input as {
        "action": "billing.account.read",
        "principal": {"tenant_id": "tenant-a"},
        "resource": {"tenant_id": "tenant-a"},
        "entitlements": {}
    }
}
