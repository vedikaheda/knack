import { appendAuditEvent } from "../lib/audit";
import { getConfig, requireConfig } from "../lib/config";
import { createProofDocument, storeProofOwnerSecret } from "../lib/proof";

type CreateProofDocumentArgs = {
  title: string;
  markdown: string;
  role?: string;
};

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
        const baseUrl = requireConfig(api, "PROOF_BASE_URL");
        const storePath = getConfig(
          api,
          "PROOF_OWNER_SECRET_STORE_PATH",
          ".local/proof/owner-secrets.json"
        )!;
        const payload = await createProofDocument(
          baseUrl,
          params.markdown,
          params.title,
          params.role ?? "editor"
        );

        if (!payload.ownerSecret) {
          throw new Error("Proof document creation failed: missing ownerSecret in response");
        }

        await storeProofOwnerSecret(storePath, {
          slug: payload.slug,
          title: params.title,
          ownerSecret: payload.ownerSecret,
          accessToken: payload.accessToken,
          shareUrl: payload.shareUrl,
          tokenUrl: payload.tokenUrl,
          createdAt: new Date().toISOString(),
        });

        const documentUrl = payload.tokenUrl ?? payload.shareUrl;

        await appendAuditEvent(api, {
          event: "proof.create_document",
          status: "success",
          details: {
            slug: payload.slug,
            title: params.title,
            document_url: documentUrl,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: documentUrl
                ? `Created your Proof document: ${documentUrl}`
                : `Created your Proof document "${params.title}".`,
            },
          ],
          structuredContent: {
            slug: payload.slug,
            title: params.title,
            document_url: documentUrl,
            share_url: payload.shareUrl ?? null,
            token_url: payload.tokenUrl ?? null,
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
