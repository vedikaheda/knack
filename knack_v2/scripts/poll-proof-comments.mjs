import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const TRACKED_DOCS_PATH =
  process.env.TRACKED_DOCS_PATH || "/shared-state/proof/tracked-docs.json";
const PROOF_BASE_URL = process.env.PROOF_BASE_URL || "http://proof:4000";
const OPENCLAW_HOOK_URL =
  process.env.OPENCLAW_HOOK_URL || "http://openclaw:18789/hooks/agent";
const OPENCLAW_HOOK_TOKEN = process.env.OPENCLAW_HOOK_TOKEN || "";
const POLLER_AGENT_ID = process.env.POLLER_AGENT_ID || "knack-poller";
const DEFAULT_HOOK_AGENT_ID = process.env.OPENCLAW_AGENT_ID || "main";

async function readTrackedDocs() {
  try {
    const content = await readFile(TRACKED_DOCS_PATH, "utf8");
    const parsed = JSON.parse(content);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error) {
    if (error?.code === "ENOENT") {
      return {};
    }

    throw error;
  }
}

async function writeTrackedDocs(docs) {
  const absolutePath = path.resolve(TRACKED_DOCS_PATH);
  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, JSON.stringify(docs, null, 2), "utf8");
}

function extractEvents(payload) {
  if (Array.isArray(payload?.events)) {
    return payload.events;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  if (Array.isArray(payload)) {
    return payload;
  }

  return [];
}

function extractLatestCursor(payload, fallback) {
  if (typeof payload?.nextAfter === "number") {
    return payload.nextAfter;
  }

  if (typeof payload?.after === "number") {
    return payload.after;
  }

  const events = extractEvents(payload);
  const numericIds = events
    .map((event) => event?.id)
    .filter((value) => typeof value === "number");

  return numericIds.length > 0 ? Math.max(...numericIds) : fallback;
}

function hasActionableCommentEvents(payload) {
  const events = extractEvents(payload);
  return events.some((event) => {
    const type = String(event?.type ?? "").toLowerCase();
    const actor = String(event?.actorType ?? event?.byType ?? "").toLowerCase();
    const isComment = type.includes("comment");
    const isHuman = !actor || actor.includes("human") || actor.includes("user");
    return isComment && isHuman;
  });
}

async function getPendingEvents(doc) {
  const url = new URL(`/api/agent/${doc.slug}/events/pending`, PROOF_BASE_URL);
  url.searchParams.set("after", String(doc.lastEventCursor ?? 0));
  const response = await fetch(url, {
    headers: {
      "x-share-token": doc.token,
      "X-Agent-Id": POLLER_AGENT_ID,
    },
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    throw new Error(
      `Pending events fetch failed for ${doc.slug}: HTTP ${response.status} ${text}`
    );
  }

  return payload;
}

async function triggerOpenClaw(doc, afterCursor) {
  const lines = [
    "Use the apply_proof_review_comments skill for this Proof document.",
    `proofUrl: ${doc.tokenUrl || `${PROOF_BASE_URL}/d/${doc.slug}?token=${doc.token}`}`,
    `slug: ${doc.slug}`,
    `token: ${doc.token}`,
    `after: ${afterCursor}`,
    "Check new human review comments, edit the document, resolve handled comments, and acknowledge processed events.",
    "Do not post conversational reply comments.",
  ];

  const payload = {
    name: "proof.comments.pending",
    message: lines.join("\n"),
    agentId: DEFAULT_HOOK_AGENT_ID,
    wakeMode: "now",
    deliver: Boolean(doc.routing?.to),
    channel: doc.routing?.channel || "slack",
    to: doc.routing?.to,
    accountId: doc.routing?.accountId || "default",
  };

  if (doc.routing?.sessionKey) {
    payload.sessionKey = doc.routing.sessionKey;
  }

  const response = await fetch(OPENCLAW_HOOK_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENCLAW_HOOK_TOKEN}`,
    },
    body: JSON.stringify(payload),
  });

  const body = await response.text();
  if (!response.ok) {
    throw new Error(`OpenClaw hook failed: HTTP ${response.status} ${body}`);
  }
}

async function main() {
  const docs = await readTrackedDocs();
  const now = Date.now();
  let didChange = false;

  for (const [slug, doc] of Object.entries(docs)) {
    if (!doc?.enabled) {
      continue;
    }

    if (doc.watchUntil && Date.parse(doc.watchUntil) <= now) {
      docs[slug] = {
        ...doc,
        enabled: false,
        lastCheckedAt: new Date().toISOString(),
        lastUpdatedAt: new Date().toISOString(),
      };
      didChange = true;
      continue;
    }

    const payload = await getPendingEvents(doc);
    const nextCursor = extractLatestCursor(payload, doc.lastEventCursor ?? 0);
    docs[slug] = {
      ...doc,
      lastCheckedAt: new Date().toISOString(),
      lastUpdatedAt: new Date().toISOString(),
    };
    didChange = true;

    if (!hasActionableCommentEvents(payload)) {
      continue;
    }

    await triggerOpenClaw(doc, doc.lastEventCursor ?? 0);
    docs[slug] = {
      ...docs[slug],
      lastTriggeredAt: new Date().toISOString(),
      lastUpdatedAt: new Date().toISOString(),
    };
  }

  if (didChange) {
    await writeTrackedDocs(docs);
  }
}

main().catch((error) => {
  console.error(error?.message ?? String(error));
  process.exitCode = 1;
});
