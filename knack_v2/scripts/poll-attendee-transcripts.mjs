import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const ATTENDEE_TRACKED_BOTS_PATH =
  process.env.ATTENDEE_TRACKED_BOTS_PATH || "/shared-state/attendee/tracked-bots.json";
const ATTENDEE_BASE_URL = process.env.ATTENDEE_BASE_URL || "";
const ATTENDEE_API_KEY = process.env.ATTENDEE_API_KEY || "";
const OPENCLAW_HOOK_URL =
  process.env.OPENCLAW_HOOK_URL || "http://openclaw:18789/hooks/agent";
const OPENCLAW_HOOK_TOKEN = process.env.OPENCLAW_HOOK_TOKEN || "";
const OPENCLAW_AGENT_ID = process.env.OPENCLAW_AGENT_ID || "main";

async function readTrackedBots() {
  try {
    const content = await readFile(ATTENDEE_TRACKED_BOTS_PATH, "utf8");
    const parsed = JSON.parse(content);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error) {
    if (error?.code === "ENOENT") {
      return {};
    }

    throw error;
  }
}

async function writeTrackedBots(bots) {
  const absolutePath = path.resolve(ATTENDEE_TRACKED_BOTS_PATH);
  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, JSON.stringify(bots, null, 2), "utf8");
}

async function fetchBot(botId) {
  if (!ATTENDEE_BASE_URL) {
    throw new Error("Missing ATTENDEE_BASE_URL");
  }

  if (!ATTENDEE_API_KEY) {
    throw new Error("Missing ATTENDEE_API_KEY");
  }

  const response = await fetch(new URL(`/api/v1/bots/${botId}`, ATTENDEE_BASE_URL), {
    headers: {
      Authorization: `Token ${ATTENDEE_API_KEY}`,
      "Content-Type": "application/json",
    },
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    throw new Error(`Attendee bot fetch failed for ${botId}: HTTP ${response.status} ${text}`);
  }

  return payload;
}

function isTranscriptReady(bot) {
  const state = String(bot?.state ?? "").toLowerCase();
  const transcriptionState = String(bot?.transcription_state ?? "").toLowerCase();
  return state === "ended" && (transcriptionState === "complete" || transcriptionState === "completed");
}

async function triggerOpenClaw(bot, trackedBot) {
  const lines = [
    "Use the generate_brd_from_attendee_transcript skill for this completed Attendee meeting transcript.",
    `bot_id: ${trackedBot.botId}`,
    `meeting_url: ${trackedBot.meetingUrl}`,
    "Fetch the transcript from Attendee, generate the BRD, create the Proof document, and send the Proof link back to the same user.",
    "Do not mention internal watcher or hook details in the user-facing response.",
  ];

  const payload = {
    name: "attendee.transcript.complete",
    message: lines.join("\n"),
    agentId: OPENCLAW_AGENT_ID,
    wakeMode: "now",
    deliver: Boolean(trackedBot.routing?.to),
    channel: trackedBot.routing?.channel || "slack",
    to: trackedBot.routing?.to,
    accountId: trackedBot.routing?.accountId || "default",
    metadata: {
      bot_id: trackedBot.botId,
      meeting_url: trackedBot.meetingUrl,
      attendee_state: bot?.state ?? null,
      attendee_transcription_state: bot?.transcription_state ?? null,
    },
  };

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
  const bots = await readTrackedBots();
  let didChange = false;

  for (const [botId, trackedBot] of Object.entries(bots)) {
    if (!trackedBot?.enabled) {
      continue;
    }

    const bot = await fetchBot(botId);
    bots[botId] = {
      ...trackedBot,
      state: typeof bot?.state === "string" ? bot.state : trackedBot.state,
      transcriptionState:
        typeof bot?.transcription_state === "string"
          ? bot.transcription_state
          : trackedBot.transcriptionState,
      lastCheckedAt: new Date().toISOString(),
      lastUpdatedAt: new Date().toISOString(),
    };
    didChange = true;

    if (!isTranscriptReady(bot)) {
      continue;
    }

    if (trackedBot.lastTriggeredAt) {
      continue;
    }

    await triggerOpenClaw(bot, bots[botId]);
    bots[botId] = {
      ...bots[botId],
      lastTriggeredAt: new Date().toISOString(),
      lastUpdatedAt: new Date().toISOString(),
    };
  }

  if (didChange) {
    await writeTrackedBots(bots);
  }
}

main().catch((error) => {
  console.error(error?.message ?? String(error));
  process.exitCode = 1;
});
