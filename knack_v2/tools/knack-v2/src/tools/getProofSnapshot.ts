import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { getProofSnapshot } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type GetProofSnapshotArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  agentId?: string;
};

export function registerGetProofSnapshotTool(api: any) {
  api.registerTool({
    name: "get_proof_snapshot",
    description: "Fetch a Proof document snapshot with revision and block refs",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        agentId: { type: "string" },
      },
    },
    async execute(_toolUseId: string, params: GetProofSnapshotArgs) {
      try {
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await getProofSnapshot(baseUrl, target, agentId!);

        await appendAuditEvent(api, {
          event: "proof.get_snapshot",
          status: "success",
          details: {
            slug: target.slug,
          },
        });

        const textPayload = JSON.stringify(payload, null, 2);

        return {
          content: [
            {
              type: "text",
              text: `Fetched Proof snapshot for ${target.slug}.\n\n${textPayload}`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.get_snapshot",
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
