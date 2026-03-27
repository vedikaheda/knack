import { appendAuditEvent } from "../lib/audit";
import { getAttendeeBot } from "../lib/attendee";
import { requireConfig } from "../lib/config";

type GetAttendeeBotArgs = {
  bot_id: string;
};

export function registerGetAttendeeBotTool(api: any) {
  api.registerTool({
    name: "get_attendee_bot",
    description: "Fetch Attendee bot state by bot id",
    parameters: {
      type: "object",
      properties: {
        bot_id: { type: "string" },
      },
      required: ["bot_id"],
    },
    async execute(_toolUseId: string, params: GetAttendeeBotArgs) {
      try {
        const baseUrl = requireConfig(api, "ATTENDEE_BASE_URL");
        const apiKey = requireConfig(api, "ATTENDEE_API_KEY");
        const payload = await getAttendeeBot(baseUrl, apiKey, params.bot_id);

        await appendAuditEvent(api, {
          event: "attendee.get_bot",
          status: "success",
          details: {
            bot_id: params.bot_id,
            state: payload.state ?? null,
            transcription_state: payload.transcription_state ?? null,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Fetched Attendee bot ${params.bot_id}.\n\n${JSON.stringify(payload, null, 2)}`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "attendee.get_bot",
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
