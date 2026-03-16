import { callBackendJob } from "../lib/callBackendJob";

type RegenerateBrdArgs = {
  transcript_request_id: string;
  slack_user_id?: string;
  conversation_id?: string;
  thread_ts?: string;
  slack_event_id?: string;
};

export function registerRegenerateBrdTool(api: any) {
  api.registerTool({
    name: "regenerate_brd",
    description: "Trigger backend BRD regeneration for an existing transcript request",
    parameters: {
      type: "object",
      properties: {
        transcript_request_id: {
          type: "string",
          description: "Internal transcript request identifier"
        },
        slack_user_id: { type: "string" },
        conversation_id: { type: "string" },
        thread_ts: { type: "string" },
        slack_event_id: { type: "string" }
      },
      required: ["transcript_request_id"]
    },
    async execute(_toolUseId: string, params: RegenerateBrdArgs) {
      const result = await callBackendJob(
        api,
        "regenerate_brd",
        { transcript_request_id: params.transcript_request_id },
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
              "Got it. Regenerating the BRD. I'll notify you when it's done."
          }
        ],
        structuredContent: result
      };
    }
  });
}
