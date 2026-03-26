import { appendAuditEvent } from "../lib/audit";
import { getConfig } from "../lib/config";
import { updateTrackedProofDocument } from "../lib/proofTracking";

function extractProofSlug(content: string): string | null {
  const match = content.match(/\/d\/([a-z0-9]+)\?token=/i);
  return match?.[1] ?? null;
}

export function registerProofRoutingHook(api: any) {
  api.registerHook(
    "message_sent",
    async (event: any, ctx: any) => {
      if (event?.success === false) {
        return;
      }

      const channelId = ctx?.channelId;
      const content = String(event?.content ?? "");

      if (channelId !== "slack" || !content.includes("/d/")) {
        return;
      }

      const slug = extractProofSlug(content);
      if (!slug) {
        return;
      }

      const trackedDocsPath = getConfig(
        api,
        "PROOF_TRACKED_DOCS_PATH",
        ".local/proof/tracked-docs.json"
      )!;

      const updated = await updateTrackedProofDocument(trackedDocsPath, slug, {
        routing: {
          channel: channelId,
          to: event?.to ?? null,
          accountId: ctx?.accountId ?? "default",
          sessionKey: event?.sessionKey ?? null,
          conversationId: ctx?.conversationId ?? null,
        },
      });

      await appendAuditEvent(api, {
        event: "proof.capture_routing",
        status: updated ? "success" : "failure",
        details: {
          slug,
          session_key: event?.sessionKey ?? null,
          to: event?.to ?? null,
          channel: channelId,
          account_id: ctx?.accountId ?? "default",
          conversation_id: ctx?.conversationId ?? null,
          tracked_doc_found: Boolean(updated),
        },
      });
    },
    {
      name: "knack-v2.proof-routing",
      description:
        "Capture Slack session routing for newly sent Proof document links so review updates return to the same conversation.",
    }
  );
}
