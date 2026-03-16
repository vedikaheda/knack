import { callBackendJob } from "../lib/callBackendJob";

type CreateBrdArgs = {
  transcript_link: string;
  channel?: string;
  to?: string;
  account_id?: string;
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
        channel: { type: "string" },
        to: { type: "string" },
        account_id: { type: "string" }
      },
      required: ["transcript_link"]
    },
    async execute(_toolUseId: string, params: CreateBrdArgs) {
      const result = await callBackendJob(
        api,
        "create_brd_from_transcript",
        { transcript_link: params.transcript_link },
        {
          channel: params.channel,
          to: params.to,
          account_id: params.account_id,
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
