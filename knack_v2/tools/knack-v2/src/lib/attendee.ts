type AttendeeBot = {
  id?: string;
  meeting_url?: string;
  state?: string;
  transcription_state?: string;
  [key: string]: unknown;
};

export type AttendeeTranscriptEntry = {
  speaker_name?: string | null;
  speaker_uuid?: string | null;
  speaker_user_uuid?: string | null;
  timestamp_ms?: number | null;
  duration_ms?: number | null;
  transcription?: string | { transcript?: string | null; [key: string]: unknown } | null;
  [key: string]: unknown;
};

function buildAttendeeHeaders(apiKey: string): Record<string, string> {
  return {
    Authorization: `Token ${apiKey}`,
    "Content-Type": "application/json",
  };
}

async function parseAttendeeResponse(response: Response): Promise<any> {
  const text = await response.text();

  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return text;
  }
}

export async function startAttendeeBot(
  baseUrl: string,
  apiKey: string,
  meetingUrl: string,
  botName: string,
  languageCode: string,
  model: string
): Promise<AttendeeBot> {
  const response = await fetch(new URL("/api/v1/bots", baseUrl), {
    method: "POST",
    headers: buildAttendeeHeaders(apiKey),
    body: JSON.stringify({
      meeting_url: meetingUrl,
      bot_name: botName,
      transcription_settings: {
        sarvam: {
          language_code: languageCode,
          model,
        },
      },
    }),
  });

  const payload = await parseAttendeeResponse(response);

  if (!response.ok) {
    throw new Error(
      `Attendee bot start failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  if (!payload?.id) {
    throw new Error("Attendee bot start failed: missing bot id in response");
  }

  return payload;
}

export async function getAttendeeBot(
  baseUrl: string,
  apiKey: string,
  botId: string
): Promise<AttendeeBot> {
  const response = await fetch(new URL(`/api/v1/bots/${botId}`, baseUrl), {
    headers: buildAttendeeHeaders(apiKey),
  });

  const payload = await parseAttendeeResponse(response);

  if (!response.ok) {
    throw new Error(
      `Attendee bot fetch failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  return payload;
}

export async function getAttendeeTranscript(
  baseUrl: string,
  apiKey: string,
  botId: string
): Promise<AttendeeTranscriptEntry[]> {
  const response = await fetch(new URL(`/api/v1/bots/${botId}/transcript`, baseUrl), {
    headers: buildAttendeeHeaders(apiKey),
  });

  const payload = await parseAttendeeResponse(response);

  if (!response.ok) {
    throw new Error(
      `Attendee transcript fetch failed: HTTP ${response.status} ${
        typeof payload === "string" ? payload : JSON.stringify(payload)
      }`
    );
  }

  if (!Array.isArray(payload)) {
    throw new Error("Attendee transcript fetch failed: expected an array response");
  }

  return payload;
}

export function renderAttendeeTranscriptText(entries: AttendeeTranscriptEntry[]): string {
  return entries
    .map((entry) => {
      const speaker = String(entry.speaker_name ?? "Speaker").trim() || "Speaker";
      const transcriptionValue = entry.transcription;
      const text =
        typeof transcriptionValue === "string"
          ? transcriptionValue.trim()
          : typeof transcriptionValue?.transcript === "string"
          ? transcriptionValue.transcript.trim()
          : "";

      return text ? `${speaker}: ${text}` : "";
    })
    .filter(Boolean)
    .join("\n");
}
