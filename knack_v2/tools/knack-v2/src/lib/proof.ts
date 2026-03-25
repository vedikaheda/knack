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

type StoredProofSecret = {
  slug: string;
  title: string;
  ownerSecret: string;
  accessToken?: string;
  shareUrl?: string;
  tokenUrl?: string;
  createdAt: string;
};

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
