import { describe, expect, it } from "vitest";
import { CloudspaceClient } from "./index.js";

describe("CloudspaceClient", () => {
  it("reads normalized identity", async () => {
    const client = new CloudspaceClient("https://cloudspace.test", "token", async () => new Response(JSON.stringify({ principal: { id: "u1", type: "user", issuer: "issuer", attributes: {} } }), { status: 200 }));
    expect((await client.me()).principal.id).toBe("u1");
  });
});
