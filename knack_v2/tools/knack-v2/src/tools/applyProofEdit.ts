import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { applyProofDocumentEdit } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type ApplyProofEditArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  instruction: string;
  agentId?: string;
};

export function registerApplyProofEditTool(api: any) {
  api.registerTool({
    name: "apply_proof_edit",
    description: "Apply an edit instruction to a Proof document",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        instruction: { type: "string" },
        agentId: { type: "string" },
      },
      required: ["instruction"],
    },
    async execute(_toolUseId: string, params: ApplyProofEditArgs) {
      try {
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await applyProofDocumentEdit(
          baseUrl,
          target,
          agentId!,
          params.instruction
        );

        await appendAuditEvent(api, {
          event: "proof.apply_edit",
          status: "success",
          details: {
            slug: target.slug,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Applied an edit to Proof document ${target.slug}.`,
            },
          ],
          structuredContent: payload,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.apply_edit",
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
