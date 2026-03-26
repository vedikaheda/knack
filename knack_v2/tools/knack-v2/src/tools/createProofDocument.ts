import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { createProofDocument, rewriteProofUrl, storeProofOwnerSecret } from "../lib/proof";
import { storeTrackedProofDocument } from "../lib/proofTracking";

type CreateProofDocumentArgs = {
  title: string;
  markdown: string;
  role?: string;
};

function normalizeProofMarkdown(markdown: string): string {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const normalized = lines.map((line) => {
    const numberedMatch = line.match(/^(\s*)(\d+)\.\s+(.+)$/);
    if (numberedMatch) {
      const [, indent, number, content] = numberedMatch;
      return indent.length > 0
        ? `Detail ${number}: ${content.trim()}`
        : `Step ${number}: ${content.trim()}`;
    }

    const bulletMatch = line.match(/^(\s*)[*+-]\s+(.+)$/);
    if (bulletMatch) {
      const [, indent, content] = bulletMatch;
      return indent.length > 0
        ? `Detail: ${content.trim()}`
        : `Item: ${content.trim()}`;
    }

    return line;
  });

  return normalized.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

export function registerCreateProofDocumentTool(api: any) {
  api.registerTool({
    name: "create_proof_document",
    description: "Create a Proof document from markdown and store the owner secret locally",
    parameters: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "The document title",
        },
        markdown: {
          type: "string",
          description: "Full markdown content for the new document",
        },
        role: {
          type: "string",
          description: "Optional default access role for the created share link",
          enum: ["viewer", "commenter", "editor"],
        },
      },
      required: ["title", "markdown"],
    },
    async execute(_toolUseId: string, params: CreateProofDocumentArgs) {
      try {
        await appendAuditEvent(api, {
          event: "debug.tool_context",
          status: "success",
          details: {
            tool: "create_proof_document",
            api_keys: Object.keys(api ?? {}).sort(),
            session: api?.session ?? null,
            context: api?.context ?? null,
            channel: api?.channel ?? null,
            accountId: api?.accountId ?? null,
            message: api?.message ?? null,
          },
        });

        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const publicUrl = getConfig(api, "PROOF_PUBLIC_URL");
        const storePath = getConfig(
          api,
          "PROOF_OWNER_SECRET_STORE_PATH",
          ".local/proof/owner-secrets.json"
        )!;
        const trackedDocsPath = getConfig(
          api,
          "PROOF_TRACKED_DOCS_PATH",
          ".local/proof/tracked-docs.json"
        )!;
        const payload = await createProofDocument(
          baseUrl,
          normalizeProofMarkdown(params.markdown),
          params.title,
          params.role ?? "editor"
        );

        if (!payload.ownerSecret) {
          throw new Error("Proof document creation failed: missing ownerSecret in response");
        }

        const shareUrl = rewriteProofUrl(payload.shareUrl, publicUrl);
        const tokenUrl = rewriteProofUrl(payload.tokenUrl, publicUrl);

        await storeProofOwnerSecret(storePath, {
          slug: payload.slug,
          title: params.title,
          ownerSecret: payload.ownerSecret,
          accessToken: payload.accessToken,
          shareUrl,
          tokenUrl,
          createdAt: new Date().toISOString(),
        });

        const documentUrl = tokenUrl ?? shareUrl;
        const createdAt = new Date().toISOString();
        const watchDays = Number(getConfig(api, "KNACK_REVIEW_WATCH_DAYS", "7") ?? "7");
        const watchUntil = new Date(Date.now() + watchDays * 24 * 60 * 60 * 1000).toISOString();

        await appendAuditEvent(api, {
          event: "proof.create_document",
          status: "success",
          details: {
            slug: payload.slug,
            title: params.title,
            document_url: documentUrl,
          },
        });

        if (payload.accessToken) {
          await storeTrackedProofDocument(trackedDocsPath, {
            slug: payload.slug,
            title: params.title,
            token: payload.accessToken,
            shareUrl,
            tokenUrl,
            createdAt,
            watchUntil,
            pollEveryMinutes: 15,
            lastEventCursor: 0,
            enabled: true,
            routing: {
              channel: getConfig(api, "KNACK_SLACK_CHANNEL", "slack"),
              to: getConfig(api, "KNACK_SLACK_TO"),
              accountId: getConfig(api, "KNACK_SLACK_ACCOUNT_ID", "default"),
              sessionKey: getConfig(api, "KNACK_SESSION_KEY"),
            },
            lastUpdatedAt: createdAt,
          });
        }

        return {
          content: [
            {
              type: "text",
              text: documentUrl
                ? `Created your Proof document:\n<${documentUrl}|Open the BRD>`
                : `Created your Proof document "${params.title}".`,
            },
          ],
          structuredContent: {
            slug: payload.slug,
            title: params.title,
            document_url: documentUrl,
            slack_link: documentUrl ? `<${documentUrl}|Open the BRD>` : null,
            share_url: shareUrl ?? null,
            token_url: tokenUrl ?? null,
            access_role: payload.accessRole ?? params.role ?? "commenter",
            owner_secret_stored: true,
          },
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "proof.create_document",
          status: "failure",
          details: {
            title: params.title,
            error: message,
          },
        });

        throw new Error(message);
      }
    },
  });
}
