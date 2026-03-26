import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

export type ProofRouting = {
  channel?: string;
  to?: string;
  accountId?: string;
  sessionKey?: string;
};

export type TrackedProofDocument = {
  slug: string;
  title: string;
  token: string;
  shareUrl?: string;
  tokenUrl?: string;
  createdAt: string;
  watchUntil: string;
  pollEveryMinutes: number;
  lastEventCursor: number;
  enabled: boolean;
  routing?: ProofRouting;
  lastCheckedAt?: string;
  lastTriggeredAt?: string;
  lastUpdatedAt: string;
};

async function readTrackedDocs(
  filePath: string
): Promise<Record<string, TrackedProofDocument>> {
  try {
    const content = await readFile(filePath, "utf8");
    const parsed = JSON.parse(content);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error: any) {
    if (error?.code === "ENOENT") {
      return {};
    }

    throw new Error(`Failed to read tracked Proof docs: ${error?.message ?? String(error)}`);
  }
}

async function writeTrackedDocs(
  filePath: string,
  docs: Record<string, TrackedProofDocument>
): Promise<void> {
  const absolutePath = path.resolve(filePath);
  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, JSON.stringify(docs, null, 2), "utf8");
}

export async function storeTrackedProofDocument(
  filePath: string,
  doc: TrackedProofDocument
): Promise<void> {
  const absolutePath = path.resolve(filePath);
  const docs = await readTrackedDocs(absolutePath);
  docs[doc.slug] = doc;
  await writeTrackedDocs(absolutePath, docs);
}

export async function updateTrackedProofDocument(
  filePath: string,
  slug: string,
  update: Partial<TrackedProofDocument>
): Promise<TrackedProofDocument | null> {
  const absolutePath = path.resolve(filePath);
  const docs = await readTrackedDocs(absolutePath);
  const existing = docs[slug];

  if (!existing) {
    return null;
  }

  const merged: TrackedProofDocument = {
    ...existing,
    ...update,
    slug: existing.slug,
    lastUpdatedAt: new Date().toISOString(),
  };

  docs[slug] = merged;
  await writeTrackedDocs(absolutePath, docs);
  return merged;
}

export async function listTrackedProofDocuments(
  filePath: string
): Promise<TrackedProofDocument[]> {
  const docs = await readTrackedDocs(path.resolve(filePath));
  return Object.values(docs);
}
