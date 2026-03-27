import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

export type TrackedAttendeeRouting = {
  channel?: string;
  to?: string;
  accountId?: string;
};

export type TrackedAttendeeBot = {
  botId: string;
  meetingUrl: string;
  createdAt: string;
  state?: string;
  transcriptionState?: string;
  enabled: boolean;
  routing?: TrackedAttendeeRouting;
  lastCheckedAt?: string;
  lastTriggeredAt?: string;
  lastUpdatedAt: string;
};

async function readTrackedBots(
  filePath: string
): Promise<Record<string, TrackedAttendeeBot>> {
  try {
    const content = await readFile(filePath, "utf8");
    const parsed = JSON.parse(content);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error: any) {
    if (error?.code === "ENOENT") {
      return {};
    }

    throw new Error(`Failed to read tracked Attendee bots: ${error?.message ?? String(error)}`);
  }
}

async function writeTrackedBots(
  filePath: string,
  bots: Record<string, TrackedAttendeeBot>
): Promise<void> {
  const absolutePath = path.resolve(filePath);
  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, JSON.stringify(bots, null, 2), "utf8");
}

export async function storeTrackedAttendeeBot(
  filePath: string,
  bot: TrackedAttendeeBot
): Promise<void> {
  const absolutePath = path.resolve(filePath);
  const bots = await readTrackedBots(absolutePath);
  bots[bot.botId] = bot;
  await writeTrackedBots(absolutePath, bots);
}

export async function updateTrackedAttendeeBot(
  filePath: string,
  botId: string,
  update: Partial<TrackedAttendeeBot>
): Promise<TrackedAttendeeBot | null> {
  const absolutePath = path.resolve(filePath);
  const bots = await readTrackedBots(absolutePath);
  const existing = bots[botId];

  if (!existing) {
    return null;
  }

  const merged: TrackedAttendeeBot = {
    ...existing,
    ...update,
    botId: existing.botId,
    lastUpdatedAt: new Date().toISOString(),
  };

  bots[botId] = merged;
  await writeTrackedBots(absolutePath, bots);
  return merged;
}
