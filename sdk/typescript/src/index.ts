export type Principal = { id: string; type: "user" | "service"; issuer: string; tenant_id?: string | null; attributes: Record<string, unknown> };
export type AuthorizationCheckRequest = { principal: Principal; action: string; resource: string; context?: Record<string, unknown> };
export type AuthorizationDecision = { decision: boolean; decision_id: string; reason: string; policy_revision: string; obligations: Record<string, unknown>[] };
export type BillingOverview = { account: { id: string; owner_principal_id: string; provider?: Record<string, string> | null } | null; subscription: { id: string; billing_account_id: string; plan_id: string; status: string; provider?: Record<string, string> | null } | null };

export class CloudspaceError extends Error { constructor(public code: string, message: string, public requestId: string, public statusCode: number) { super(message); } }

export class CloudspaceClient {
  private readonly baseUrl: string;
  constructor(baseUrl: string, private readonly accessToken: string, private readonly fetcher: typeof fetch = fetch) { this.baseUrl = baseUrl.replace(/\/$/, ""); }
  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await this.fetcher(`${this.baseUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.accessToken}`, ...init.headers } });
    const body = await response.json() as T & { error?: { code?: string; message?: string; request_id?: string } };
    if (!response.ok) throw new CloudspaceError(body.error?.code ?? "INTERNAL", body.error?.message ?? "Cloudspace request failed", body.error?.request_id ?? response.headers.get("x-request-id") ?? "unknown", response.status);
    return body;
  }
  me(): Promise<{ principal: Principal }> { return this.request("/v1/me"); }
  authorize(body: AuthorizationCheckRequest): Promise<AuthorizationDecision> { return this.request("/v1/authorization/check", { method: "POST", body: JSON.stringify(body) }); }
  billingOverview(): Promise<BillingOverview> { return this.request("/v1/billing/overview"); }
}
