import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { ackProofEvents } from "../lib/proof";
import { updateTrackedProofDocument } from "../lib/proofTracking";
import { resolveProofTargetInput } from "../lib/proofTarget";

type AckProofEventsArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  after: number;
  agentId?: string;
};

export function registerAckProofEventsTool(api: any) {
  api.registerTool({
    name: "ack_proof_events",
    description: "Acknowledge processed Proof events up to the provided cursor",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        after: { type: "number" },
        agentId: { type: "string" },
      },
      required: ["after"],
    },
    async execute(_toolUseId: string, params: AckProofEventsArgs) {
      try {
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await ackProofEvents(baseUrl, target, agentId!, params.after);
        const trackedDocsPath = getConfig(
          api,
          "PROOF_TRACKED_DOCS_PATH",
          ".local/proof/tracked-docs.json"
        )!;
        await updateTrackedProofDocument(trackedDocsPath, target.slug, {
          lastEventCursor: params.after,
          lastCheckedAt: new Date().toISOString(),
        });

        await appendAuditEvent(api, {
          event: "proof.ack_events",
          status: "success",
          details: {
            slug: target.slug,
            after: params.after,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Acknowledged Proof events for ${target.slug} through ${params.after}.`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.ack_events",
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
