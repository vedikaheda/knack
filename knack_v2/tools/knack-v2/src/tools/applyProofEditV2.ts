import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { applyProofDocumentEditV2, getProofSnapshot } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type ApplyProofEditV2Args = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  baseRevision: number;
  operations: Array<Record<string, unknown>>;
  idempotencyKey?: string;
  agentId?: string;
};

export function registerApplyProofEditV2Tool(api: any) {
  api.registerTool({
    name: "apply_proof_edit_v2",
    description: "Apply block-level Proof edit v2 operations using snapshot refs",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        baseRevision: { type: "number" },
        operations: {
          type: "array",
          items: {
            type: "object",
          },
          description:
            "Proof edit/v2 operations such as replace_block, insert_after, or insert_before",
        },
        idempotencyKey: { type: "string" },
        agentId: { type: "string" },
      },
      required: ["baseRevision", "operations"],
    },
    async execute(_toolUseId: string, params: ApplyProofEditV2Args) {
      try {
        if (!params.operations.length) {
          throw new Error("Proof edit v2 requires a non-empty operations array");
        }

        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await applyProofDocumentEditV2(
          baseUrl,
          target,
          agentId!,
          params.baseRevision,
          params.operations,
          params.idempotencyKey
        );
        const postEditSnapshot = await getProofSnapshot(baseUrl, target, agentId!);

        await appendAuditEvent(api, {
          event: "proof.apply_edit_v2",
          status: "success",
          details: {
            slug: target.slug,
            baseRevision: params.baseRevision,
            operationCount: params.operations.length,
            operations: params.operations,
            postEditRevision: postEditSnapshot?.revision ?? null,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Applied ${params.operations.length} edit v2 operation(s) to Proof document ${target.slug}; fetched post-edit snapshot revision ${postEditSnapshot?.revision ?? "unknown"}.`,
            },
          ],
          structuredContent: {
            edit: payload,
            postEditSnapshot,
          },
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.apply_edit_v2",
          status: "failure",
          details: {
            baseRevision: params.baseRevision,
            operations: params.operations,
            error: message,
          },
        });

        throw new Error(message);
      }
    },
  });
}
