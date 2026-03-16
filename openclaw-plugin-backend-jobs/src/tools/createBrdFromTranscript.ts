import { callBackendJob } from "../lib/callBackendJob";

type CreateBrdArgs = {
  transcript_link: string;
  slack_user_id?: string;
  conversation_id?: string;
  thread_ts?: string;
  slack_event_id?: string;
};

export function registerCreateBrdFromTranscriptTool(api: any) {
  api.registerTool({
    name: "create_brd_from_transcript",
    description: "Trigger backend BRD generation from a Fireflies transcript link",
    parameters: {
      type: "object",
      properties: {
        transcript_link: {
          type: "string",
          description: "The Fireflies transcript URL"
        },
        slack_user_id: { type: "string" },
        conversation_id: { type: "string" },
        thread_ts: { type: "string" },
        slack_event_id: { type: "string" }
      },
      required: ["transcript_link"]
    },
    async execute(_toolUseId: string, params: CreateBrdArgs) {
      const result = await callBackendJob(
        api,
        "create_brd_from_transcript",
        { transcript_link: params.transcript_link },
        {
          slack_user_id: params.slack_user_id,
          conversation_id: params.conversation_id,
          thread_ts: params.thread_ts,
          slack_event_id: params.slack_event_id,
        }
      );

      return {
        content: [
          {
            type: "text",
            text:
              result.message ??
              "Got it. I'm generating your BRD and will notify you when it's ready..."
          }
        ],
        structuredContent: result
      };
    }
  });
}
