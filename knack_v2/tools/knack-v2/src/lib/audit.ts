import { mkdir, appendFile } from "node:fs/promises";
import path from "node:path";
import { getConfig } from "./config";

type AuditEvent = {
  event: string;
  status: "success" | "failure";
  details: Record<string, unknown>;
};

export async function appendAuditEvent(api: any, payload: AuditEvent): Promise<void> {
  const logPath = getConfig(api, "KNACK_AUDIT_LOG_PATH", ".local/audit/events.jsonl")!;
  const absolutePath = path.resolve(logPath);

  await mkdir(path.dirname(absolutePath), { recursive: true });

  const record = {
    timestamp: new Date().toISOString(),
    ...payload,
  };

  await appendFile(absolutePath, `${JSON.stringify(record)}\n`, "utf8");
}
