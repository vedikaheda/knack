const FIREFLIES_GRAPHQL_URL = "https://api.fireflies.ai/graphql";
const FIREFLIES_HOSTS = new Set(["app.fireflies.ai", "fireflies.ai"]);

type FirefliesTranscriptSentence = {
  index?: number | null;
  speaker_name?: string | null;
  speaker_id?: string | null;
  text?: string | null;
  start_time?: number | null;
  end_time?: number | null;
};

type FirefliesTranscriptResponse = {
  id?: string | null;
  title?: string | null;
  date?: string | null;
  duration?: number | null;
  meeting_link?: string | null;
  sentences?: FirefliesTranscriptSentence[] | null;
};

export function parseTranscriptId(link: string): string {
  let url: URL;

  try {
    url = new URL(link);
  } catch {
    throw new Error("Invalid transcript link: expected a valid URL");
  }

  if (!FIREFLIES_HOSTS.has(url.hostname)) {
    throw new Error("Invalid transcript link: expected a Fireflies URL");
  }

  const segments = url.pathname.split("/").filter(Boolean);
  const viewIndex = segments.findIndex((segment) => segment === "view");
  const transcriptId = viewIndex >= 0 ? segments[viewIndex + 1] : segments.at(-1);

  if (!transcriptId) {
    throw new Error("Invalid transcript link: could not parse transcript id");
  }

  return transcriptId;
}

export async function fetchTranscript(apiKey: string, transcriptId: string): Promise<FirefliesTranscriptResponse> {
  const query = `
    query Transcript($id: String!) {
      transcript(id: $id) {
        id
        title
        date
        duration
        meeting_link
        sentences {
          index
          speaker_name
          speaker_id
          text
          start_time
          end_time
        }
      }
    }
  `;

  const response = await fetch(FIREFLIES_GRAPHQL_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      query,
      variables: { id: transcriptId },
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Fireflies request failed: HTTP ${response.status} ${body}`);
  }

  const payload = await response.json();

  if (payload.errors?.length) {
    throw new Error(`Fireflies API error: ${JSON.stringify(payload.errors)}`);
  }

  const transcript = payload.data?.transcript;

  if (!transcript) {
    throw new Error("Fireflies transcript not found");
  }

  return transcript;
}

export function renderTranscriptText(transcript: FirefliesTranscriptResponse): string {
  const sentences = transcript.sentences ?? [];

  return sentences
    .map((sentence) => {
      const speaker = sentence.speaker_name?.trim() || "Speaker";
      const text = sentence.text?.trim() || "";
      return text ? `${speaker}: ${text}` : "";
    })
    .filter(Boolean)
    .join("\n");
}

export function cleanTranscriptText(text: string): string {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .join("\n");
}
