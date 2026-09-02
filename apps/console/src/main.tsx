import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import "./style.css";

const client = new QueryClient();
const api = async <T,>(path: string): Promise<T> => {
  const response = await fetch(path, { headers: { Authorization: "Bearer dev-user-alice" } });
  if (!response.ok) throw new Error("The platform API could not complete this request.");
  return response.json() as Promise<T>;
};

function Shell() {
  return <main><nav><strong>Cloudspace</strong><span><Link to="/">Account</Link><Link to="/billing">Billing</Link></span></nav><Routes><Route path="/" element={<Account />} /><Route path="/billing" element={<Billing />} /></Routes></main>;
}

function Account() {
  const result = useQuery({ queryKey: ["me"], queryFn: () => api<{principal: {id: string; type: string; tenant_id?: string}}>("/v1/me") });
  if (result.isLoading) return <section className="card">Loading account…</section>;
  if (result.isError) return <section className="card error">Authentication or API error. Please sign in again.</section>;
  if (!result.data) return <section className="card error">Account data is empty.</section>;
  return <section className="card"><p className="eyebrow">Account</p><h1>Welcome back</h1><p>Signed in as <code>{result.data.principal.id}</code></p><p className="muted">Tenant: {result.data.principal.tenant_id ?? "none"}</p></section>;
}

function Billing() {
  const result = useQuery({ queryKey: ["billing"], queryFn: () => api<{account: {id: string} | null; subscription: {plan_id: string; status: string} | null}>("/v1/billing/overview") });
  if (result.isLoading) return <section className="card">Loading billing…</section>;
  if (result.isError) return <section className="card error">Billing data is temporarily unavailable.</section>;
  if (!result.data) return <section className="card error">Billing data is empty.</section>;
  return <section className="card"><p className="eyebrow">Billing overview</p><h1>{result.data.subscription?.plan_id ?? "No plan"}</h1><p>Status: <span className="badge">{result.data.subscription?.status ?? "not configured"}</span></p><p className="muted">Account: {result.data.account?.id ?? "none"}</p></section>;
}

createRoot(document.getElementById("root")!).render(<StrictMode><QueryClientProvider client={client}><BrowserRouter><Shell /></BrowserRouter></QueryClientProvider></StrictMode>);
