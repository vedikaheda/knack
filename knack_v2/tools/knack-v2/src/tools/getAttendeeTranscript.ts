import { appendAuditEvent } from "../lib/audit";
import {
  AttendeeTranscriptEntry,
  getAttendeeTranscript,
  renderAttendeeTranscriptText,
} from "../lib/attendee";
import { cleanTranscriptText } from "../lib/fireflies";
import { requireConfig } from "../lib/config";

type GetAttendeeTranscriptArgs = {
  bot_id: string;
};

function firstTimestamp(entries: AttendeeTranscriptEntry[]): number | null {
  const values = entries
    .map((entry) => entry.timestamp_ms)
    .filter((value): value is number => typeof value === "number");
  return values.length ? Math.min(...values) : null;
}

export function registerGetAttendeeTranscriptTool(api: any) {
  api.registerTool({
    name: "get_attendee_transcript",
    description: "Fetch and normalize an Attendee transcript by bot id",
    parameters: {
      type: "object",
      properties: {
        bot_id: { type: "string" },
      },
      required: ["bot_id"],
    },
    async execute(_toolUseId: string, params: GetAttendeeTranscriptArgs) {
      try {
        const baseUrl = requireConfig(api, "ATTENDEE_BASE_URL");
        const apiKey = requireConfig(api, "ATTENDEE_API_KEY");
        const entries = await getAttendeeTranscript(baseUrl, apiKey, params.bot_id);
        const rawTranscript = renderAttendeeTranscriptText(entries);
        const cleanedTranscript = cleanTranscriptText(rawTranscript);

        const result = {
          bot_id: params.bot_id,
          utterance_count: entries.length,
          first_timestamp_ms: firstTimestamp(entries),
          raw_transcript: rawTranscript,
          cleaned_transcript: cleanedTranscript,
          entries,
        };

        await appendAuditEvent(api, {
          event: "attendee.get_transcript",
          status: "success",
          details: {
            bot_id: params.bot_id,
            utterance_count: entries.length,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Fetched Attendee transcript for bot ${params.bot_id}.`,
            },
            {
              type: "text",
              text: `Utterances: ${entries.length}\n\nCleaned transcript:\n${cleanedTranscript}`,
            },
          ],
          structuredContent: result,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "attendee.get_transcript",
          status: "failure",
          details: {
            bot_id: params.bot_id,
            error: message,
          },
        });

        throw new Error(message);
      }
    },
  });
}
