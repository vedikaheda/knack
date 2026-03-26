import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { getProofDocumentState } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type GetProofDocumentStateArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  agentId?: string;
};

export function registerGetProofDocumentStateTool(api: any) {
  api.registerTool({
    name: "get_proof_document_state",
    description: "Fetch Proof document state for a tokenized doc URL or slug/token pair",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        agentId: { type: "string" },
      },
    },
    async execute(_toolUseId: string, params: GetProofDocumentStateArgs) {
      try {
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await getProofDocumentState(baseUrl, target, agentId!);

        await appendAuditEvent(api, {
          event: "proof.get_document_state",
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
              text: `Fetched Proof document state for ${target.slug}.\n\n${textPayload}`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.get_document_state",
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
