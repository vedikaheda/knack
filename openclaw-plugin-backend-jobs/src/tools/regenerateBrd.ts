import { callBackendJob } from "../lib/callBackendJob";

type RegenerateBrdArgs = {
  transcript_request_id: string;
  channel?: string;
  to?: string;
  account_id?: string;
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
        channel: { type: "string" },
        to: { type: "string" },
        account_id: { type: "string" }
      },
      required: ["transcript_request_id"]
    },
    async execute(_toolUseId: string, params: RegenerateBrdArgs) {
      const result = await callBackendJob(
        api,
        "regenerate_brd",
        { transcript_request_id: params.transcript_request_id },
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
              "Got it. Regenerating the BRD. I'll notify you when it's done."
          }
        ],
        structuredContent: result
      };
    }
  });
}
