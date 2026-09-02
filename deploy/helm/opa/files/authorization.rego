package cloudspace.authorization

default allow := false

allow if {
    input.action == "billing.account.read"
    input.resource == sprintf("billing-account:%s", [input.principal.tenant_id])
    input.entitlements.billing_read == true
}
