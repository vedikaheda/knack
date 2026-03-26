import { randomUUID } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

export type ProofCreateDocumentResult = {
  slug: string;
  shareUrl?: string;
  tokenUrl?: string;
  ownerSecret?: string;
  accessToken?: string;
  accessRole?: string;
};

export type ProofTarget = {
  slug: string;
  token: string;
};

type StoredProofSecret = {
  slug: string;
  title: string;
  ownerSecret: string;
  accessToken?: string;
  shareUrl?: string;
  tokenUrl?: string;
  createdAt: string;
};

function buildProofHeaders(token: string, agentId?: string): Record<string, string> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
  };

  if (agentId) {
    headers["X-Agent-Id"] = agentId;
  }

  return headers;
}

async function parseProofResponse(response: Response): Promise<any> {
  const text = await response.text();

  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return text;
  }
}

export function parseProofUrl(url: string): ProofTarget {
  const parsed = new URL(url);
  const token = parsed.searchParams.get("token");
  const parts = parsed.pathname.split("/").filter(Boolean);
  const dIndex = parts.findIndex((part) => part === "d");
  const slug = dIndex >= 0 ? parts[dIndex + 1] : parts.at(-1);

  if (!slug || !token) {
    throw new Error("Proof URL must include both slug and token");
  }

  return {
    slug,
    token,
  };
}

export async function createProofDocument(
  baseUrl: string,
  markdown: string,
  title: string,
  role = "commenter"
): Promise<ProofCreateDocumentResult> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  const response = await fetch(new URL("/documents", baseUrl), {
    method: "POST",
    headers,
    body: JSON.stringify({
      title,
      markdown,
      role,
      ownerId: "agent:knack-v2",
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Proof document creation failed: HTTP ${response.status} ${body}`);
  }

  const payload = await response.json();

  if (!payload.success || !payload.slug) {
    throw new Error("Proof document creation failed: missing slug in response");
  }

  return payload;
}

export async function getProofDocumentState(
  baseUrl: string,
  target: ProofTarget,
  agentId: string
): Promise<any> {
  const response = await fetch(new URL(`/documents/${target.slug}/state`, baseUrl), {
    headers: buildProofHeaders(target.token, agentId),
  });

  const payload = await parseProofResponse(response);

  if (!response.ok) {
    throw new Error(
      `Proof state fetch failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export async function getProofSnapshot(
  baseUrl: string,
  target: ProofTarget,
  agentId: string
): Promise<any> {
  const response = await fetch(new URL(`/documents/${target.slug}/snapshot`, baseUrl), {
    headers: buildProofHeaders(target.token, agentId),
  });

  const payload = await parseProofResponse(response);

  if (!response.ok) {
    throw new Error(
      `Proof snapshot fetch failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export async function getProofPendingEvents(
  baseUrl: string,
  target: ProofTarget,
  agentId: string,
  after = 0
): Promise<any> {
  const url = new URL(`/documents/${target.slug}/events/pending`, baseUrl);
  url.searchParams.set("after", String(after));

  const response = await fetch(url, {
    headers: buildProofHeaders(target.token, agentId),
  });

  const payload = await parseProofResponse(response);

  if (!response.ok) {
    throw new Error(
      `Proof pending events fetch failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export async function applyProofDocumentEdit(
  baseUrl: string,
  target: ProofTarget,
  agentId: string,
  operations: unknown[],
  baseUpdatedAt?: string
): Promise<any> {
  const response = await fetch(new URL(`/documents/${target.slug}/edit`, baseUrl), {
    method: "POST",
    headers: {
      ...buildProofHeaders(target.token, agentId),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      by: `ai:${agentId}`,
      ...(baseUpdatedAt ? { baseUpdatedAt } : {}),
      operations,
    }),
  });

  const payload = await parseProofResponse(response);

  if (!response.ok) {
    throw new Error(
      `Proof edit failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export async function applyProofDocumentEditV2(
  baseUrl: string,
  target: ProofTarget,
  agentId: string,
  baseRevision: number,
  operations: unknown[],
  idempotencyKey?: string
): Promise<any> {
  const response = await fetch(new URL(`/documents/${target.slug}/edit/v2`, baseUrl), {
    method: "POST",
    headers: {
      ...buildProofHeaders(target.token, agentId),
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey ?? randomUUID(),
    },
    body: JSON.stringify({
      by: `ai:${agentId}`,
      baseRevision,
      operations,
    }),
  });

  const payload = await parseProofResponse(response);

  if (!response.ok) {
    throw new Error(
      `Proof edit v2 failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export async function applyProofOps(
  baseUrl: string,
  target: ProofTarget,
  agentId: string,
  ops: unknown[]
): Promise<any> {
  const results: any[] = [];

  for (const op of ops) {
    const payloadWithBy =
      op && typeof op === "object" && !Array.isArray(op)
        ? {
            by: `ai:${agentId}`,
            ...(op as Record<string, unknown>),
          }
        : op;

    const response = await fetch(new URL(`/documents/${target.slug}/ops`, baseUrl), {
      method: "POST",
      headers: {
        ...buildProofHeaders(target.token, agentId),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payloadWithBy),
    });

    const payload = await parseProofResponse(response);

    if (!response.ok) {
      throw new Error(
        `Proof ops failed: HTTP ${response.status} ${
          typeof payload === "string" ? payload : JSON.stringify(payload)
        }`
      );
    }

    results.push(payload);
  }

  return {
    success: true,
    count: results.length,
    results,
  };
}

export async function ackProofEvents(
  baseUrl: string,
  target: ProofTarget,
  agentId: string,
  after: number
): Promise<any> {
  const response = await fetch(new URL(`/documents/${target.slug}/events/ack`, baseUrl), {
    method: "POST",
    headers: {
      ...buildProofHeaders(target.token, agentId),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      upToId: after,
      by: `ai:${agentId}`,
    }),
  });

  const payload = await parseProofResponse(response);

  if (!response.ok) {
    throw new Error(
      `Proof event ack failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export function rewriteProofUrl(url: string | undefined, publicBaseUrl?: string): string | undefined {
  if (!url || !publicBaseUrl) {
    return url;
  }

  try {
    const original = new URL(url);
    const publicBase = new URL(publicBaseUrl);
    original.protocol = publicBase.protocol;
    original.host = publicBase.host;
    return original.toString();
  } catch {
    return url;
  }
}

export async function storeProofOwnerSecret(
  storePath: string,
  payload: StoredProofSecret
): Promise<void> {
  const absolutePath = path.resolve(storePath);
  await mkdir(path.dirname(absolutePath), { recursive: true });

  const existing = await readSecretStore(absolutePath);
  existing[payload.slug] = payload;

  await writeFile(absolutePath, JSON.stringify(existing, null, 2), "utf8");
}

async function readSecretStore(filePath: string): Promise<Record<string, StoredProofSecret>> {
  try {
    const content = await readFile(filePath, "utf8");
    const parsed = JSON.parse(content);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error: any) {
    if (error?.code === "ENOENT") {
      return {};
    }

    throw new Error(`Failed to read Proof owner secret store: ${error?.message ?? String(error)}`);
  }
}
