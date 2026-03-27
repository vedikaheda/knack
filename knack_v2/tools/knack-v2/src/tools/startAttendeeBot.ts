import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { startAttendeeBot } from "../lib/attendee";
import { storeTrackedAttendeeBot } from "../lib/attendeeTracking";

type StartAttendeeBotArgs = {
  meeting_url: string;
  bot_name?: string;
  channel?: string;
  to?: string;
  from?: string;
  chat_id?: string;
  accountId?: string;
};

function resolveRoutingTo(params: StartAttendeeBotArgs): string | undefined {
  if (params.to) {
    return params.to;
  }

  if (params.chat_id) {
    return params.chat_id;
  }

  if (!params.from) {
    return undefined;
  }

  return params.from.startsWith("user:") ? params.from : `user:${params.from}`;
}

export function registerStartAttendeeBotTool(api: any) {
  api.registerTool({
    name: "start_attendee_bot",
    description: "Start an Attendee bot for a Google Meet URL with Sarvam transcription",
    parameters: {
      type: "object",
      properties: {
        meeting_url: {
          type: "string",
          description: "The meeting URL to join",
        },
        bot_name: {
          type: "string",
          description: "Optional display name for the bot",
        },
        channel: { type: "string" },
        to: { type: "string" },
        from: { type: "string" },
        chat_id: { type: "string" },
        accountId: { type: "string" },
      },
      required: ["meeting_url"],
    },
    async execute(_toolUseId: string, params: StartAttendeeBotArgs) {
      try {
        const baseUrl = requireConfig(api, "ATTENDEE_BASE_URL");
        const apiKey = requireConfig(api, "ATTENDEE_API_KEY");
        const trackedBotsPath = getConfig(
          api,
          "ATTENDEE_TRACKED_BOTS_PATH",
          "/shared-state/attendee/tracked-bots.json"
        )!;
        const botName = getConfig(api, "ATTENDEE_DEFAULT_BOT_NAME", "Knack")!;
        const languageCode = getConfig(api, "ATTENDEE_SARVAM_LANGUAGE_CODE", "en-IN")!;
        const model = getConfig(api, "ATTENDEE_SARVAM_MODEL", "saarika:v2.5")!;
        const routingTo = resolveRoutingTo(params);

        const payload = await startAttendeeBot(
          baseUrl,
          apiKey,
          params.meeting_url,
          params.bot_name ?? botName,
          languageCode,
          model
        );

        const createdAt = new Date().toISOString();

        await storeTrackedAttendeeBot(trackedBotsPath, {
          botId: payload.id!,
          meetingUrl: params.meeting_url,
          createdAt,
          state: String(payload.state ?? ""),
          transcriptionState: String(payload.transcription_state ?? ""),
          enabled: true,
          routing:
            params.channel || routingTo || params.accountId
              ? {
                  channel: params.channel,
                  to: routingTo,
                  accountId: params.accountId,
                }
              : undefined,
          lastUpdatedAt: createdAt,
        });

        await appendAuditEvent(api, {
          event: "attendee.start_bot",
          status: "success",
          details: {
            bot_id: payload.id,
            meeting_url: params.meeting_url,
            state: payload.state ?? null,
            transcription_state: payload.transcription_state ?? null,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Started Attendee bot ${payload.id} for the meeting.`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "attendee.start_bot",
          status: "failure",
          details: {
            meeting_url: params.meeting_url,
            error: message,
          },
        });

        throw new Error(message);
      }
    },
  });
}
