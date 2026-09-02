package cloudspace.authorization

default allow := false

allow if {
    input.action == "billing.account.read"
    input.principal.tenant_id == input.resource.tenant_id
    input.entitlements.billing_read == true
}
