import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { getProofPendingEvents } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type GetProofPendingEventsArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  after?: number;
  agentId?: string;
};

export function registerGetProofPendingEventsTool(api: any) {
  api.registerTool({
    name: "get_proof_pending_events",
    description: "Fetch pending Proof events for a tokenized doc URL or slug/token pair",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        after: { type: "number" },
        agentId: { type: "string" },
      },
    },
    async execute(_toolUseId: string, params: GetProofPendingEventsArgs) {
      try {
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await getProofPendingEvents(
          baseUrl,
          target,
          agentId!,
          params.after ?? 0
        );

        await appendAuditEvent(api, {
          event: "proof.get_pending_events",
          status: "success",
          details: {
            slug: target.slug,
            after: params.after ?? 0,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Fetched pending Proof events for ${target.slug}.`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.get_pending_events",
          status: "failure",
          details: {
            error: message,
          },
        });

        throw new Error(message);
      }
    },
  });
}
