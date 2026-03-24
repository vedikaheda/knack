import { appendAuditEvent } from "../lib/audit";
import { requireConfig } from "../lib/config";
import {
  cleanTranscriptText,
  fetchTranscript,
  parseTranscriptId,
  renderTranscriptText,
} from "../lib/fireflies";

type FetchFirefliesTranscriptArgs = {
  transcript_link: string;
};

export function registerFetchFirefliesTranscriptTool(api: any) {
  api.registerTool({
    name: "fetch_fireflies_transcript",
    description: "Fetch a Fireflies transcript safely and return cleaned transcript text for downstream BRD generation",
    parameters: {
      type: "object",
      properties: {
        transcript_link: {
          type: "string",
          description: "The Fireflies transcript URL",
        },
      },
      required: ["transcript_link"],
    },
    async execute(_toolUseId: string, params: FetchFirefliesTranscriptArgs) {
      try {
        const apiKey = requireConfig(api, "FIREFLIES_API_KEY");
        const transcriptId = parseTranscriptId(params.transcript_link);
        const transcript = await fetchTranscript(apiKey, transcriptId);
        const rawTranscript = renderTranscriptText(transcript);
        const cleanedTranscript = cleanTranscriptText(rawTranscript);

        const result = {
          transcript_id: transcriptId,
          title: transcript.title ?? "Untitled meeting",
          date: transcript.dateString ?? null,
          summary: transcript.summary ?? null,
          raw_transcript: rawTranscript,
          cleaned_transcript: cleanedTranscript,
        };

        await appendAuditEvent(api, {
          event: "fireflies.fetch_transcript",
          status: "success",
          details: {
            transcript_id: transcriptId,
            title: result.title,
          },
        });

        return {
          content: [
            {
              type: "text",
              text: `Fetched transcript "${result.title}" and prepared it for BRD generation.`,
            },
          ],
          structuredContent: result,
        };
      } catch (error: any) {
        const message = error?.message ?? String(error);

        await appendAuditEvent(api, {
          event: "fireflies.fetch_transcript",
          status: "failure",
          details: {
            transcript_link: params.transcript_link,
            error: message,
          },
        });

        throw new Error(message);
      }
    },
  });
}
