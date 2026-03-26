import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { ackProofEvents, applyProofOps } from "../lib/proof";
import { resolveProofTargetInput } from "../lib/proofTarget";

type ApplyProofOpsArgs = {
  proofUrl?: string;
  slug?: string;
  token?: string;
  ops: unknown[];
  ackAfter?: number;
  agentId?: string;
};

export function registerApplyProofOpsTool(api: any) {
  api.registerTool({
    name: "apply_proof_ops",
    description: "Apply low-level Proof ops and optionally ack processed events",
    parameters: {
      type: "object",
      properties: {
        proofUrl: { type: "string" },
        slug: { type: "string" },
        token: { type: "string" },
        ops: {
          type: "array",
          items: {
            type: "object",
          },
        },
        ackAfter: { type: "number" },
        agentId: { type: "string" },
      },
      required: ["ops"],
    },
    async execute(_toolUseId: string, params: ApplyProofOpsArgs) {
      try {
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const target = resolveProofTargetInput(params);
        const agentId = params.agentId ?? getConfig(api, "KNACK_AGENT_ID", "knack");
        const payload = await applyProofOps(baseUrl, target, agentId!, params.ops);

        let ackPayload: any = null;
        if (typeof params.ackAfter === "number") {
          ackPayload = await ackProofEvents(baseUrl, target, agentId!, params.ackAfter);
        }

        await appendAuditEvent(api, {
          event: "proof.apply_ops",
          status: "success",
          details: {
            slug: target.slug,
            ack_after: params.ackAfter ?? null,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Applied Proof ops for ${target.slug}.`,
            },
          ],
          structuredContent: {
            ops: payload,
            ack: ackPayload,
          },
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.apply_ops",
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
