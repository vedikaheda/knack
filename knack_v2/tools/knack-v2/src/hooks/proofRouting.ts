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
    async (event: any) => {
      if (event?.type !== "message" || event?.action !== "sent") {
        return;
      }

      const channelId = event?.context?.channelId;
      const content = String(event?.context?.content ?? "");

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
          to: event?.context?.to ?? null,
          accountId: event?.context?.accountId ?? "default",
          sessionKey: event?.sessionKey ?? null,
        },
      });

      await appendAuditEvent(api, {
        event: "proof.capture_routing",
        status: updated ? "success" : "failure",
        details: {
          slug,
          session_key: event?.sessionKey ?? null,
          to: event?.context?.to ?? null,
          channel: channelId,
          account_id: event?.context?.accountId ?? "default",
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
