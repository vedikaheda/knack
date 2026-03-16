const ALLOWED_JOBS = new Set([
  "create_brd_from_transcript",
  "regenerate_brd",
]);

type BackendJobArguments = Record<string, unknown>;

type BackendJobContext = {
  slack_user_id?: string;
  conversation_id?: string;
  thread_ts?: string;
  slack_event_id?: string;
};

type BackendJobResponse = {
  status: string;
  job_execution_id?: string;
  workflow_execution_id?: string;
  message?: string;
};

type BackendJobConfig = {
  BACKEND_API_URL?: string;
  CLAWDBOT_SERVICE_TOKEN?: string;
};

function getPluginEntryConfig(api: any): BackendJobConfig {
  return (
    api?.config?.plugins?.entries?.["backend-jobs"]?.config ??
    {}
  ) as BackendJobConfig;
}

function getConfig(api: any): Required<BackendJobConfig> {
  const pluginConfig = getPluginEntryConfig(api);
  const BACKEND_API_URL =
    pluginConfig.BACKEND_API_URL ?? process.env.BACKEND_API_URL;
  const CLAWDBOT_SERVICE_TOKEN =
    pluginConfig.CLAWDBOT_SERVICE_TOKEN ?? process.env.CLAWDBOT_SERVICE_TOKEN;

  if (!BACKEND_API_URL) {
    throw new Error("BACKEND_API_URL is not configured for backend-jobs plugin");
  }

  if (!CLAWDBOT_SERVICE_TOKEN) {
    throw new Error("CLAWDBOT_SERVICE_TOKEN is not configured for backend-jobs plugin");
  }

  return {
    BACKEND_API_URL,
    CLAWDBOT_SERVICE_TOKEN,
  };
}

export async function callBackendJob(
  api: any,
  job: string,
  args: BackendJobArguments,
  context: BackendJobContext
): Promise<BackendJobResponse> {
  if (!ALLOWED_JOBS.has(job)) {
    throw new Error(`Unsupported job: ${job}`);
  }

  const { BACKEND_API_URL, CLAWDBOT_SERVICE_TOKEN } = getConfig(api);
  const endpoint = `${BACKEND_API_URL.replace(/\/$/, "")}/api/v1/jobs/execute`;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${CLAWDBOT_SERVICE_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job,
      arguments: args,
      context,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `Backend job execution failed for ${job}: ${response.status} ${response.statusText}${body ? ` - ${body}` : ""}`
    );
  }

  return (await response.json()) as BackendJobResponse;
}
