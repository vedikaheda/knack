import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { applyProofDocumentEdit } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type ApplyProofEditArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  baseUpdatedAt?: string;
  operations: Array<Record<string, unknown>>;
  agentId?: string;
};

export function registerApplyProofEditTool(api: any) {
  api.registerTool({
    name: "apply_proof_edit",
    description: "Apply structured edit operations to a Proof document",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        baseUpdatedAt: { type: "string" },
        operations: {
          type: "array",
          items: {
            type: "object",
          },
          description:
            "Structured Proof edit operations such as append, replace, or insert",
        },
        agentId: { type: "string" },
      },
      required: ["operations"],
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
          params.operations,
          params.baseUpdatedAt
        );

        await appendAuditEvent(api, {
          event: "proof.apply_edit",
          status: "success",
          details: {
            slug: target.slug,
            operationCount: params.operations.length,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Applied ${params.operations.length} edit operation(s) to Proof document ${target.slug}.`,
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
