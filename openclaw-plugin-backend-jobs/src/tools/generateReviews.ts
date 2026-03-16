function safeSerialize(value: unknown) {
  try {
    return JSON.parse(JSON.stringify(value));
  } catch {
    return String(value);
  }
}

export function registerGenerateReviewsTool(api: any) {
  api.registerTool({
    name: "generate_reviews",
    description: "Debug tool to inspect OpenClaw tool runtime arguments and context",
    parameters: {
      type: "object",
      properties: {
        topic: {
          type: "string",
          description: "Arbitrary input used only to trigger the tool"
        }
      },
      required: ["topic"]
    },
    async execute(...args: any[]) {
      const [toolUseId, params, signal, onUpdate, ctx] = args;

      const snapshot = {
        toolUseId,
        params: safeSerialize(params),
        hasSignal: Boolean(signal),
        hasOnUpdate: Boolean(onUpdate),
        ctx: safeSerialize(ctx),
        apiConfigKeys: Object.keys(api?.config ?? {}),
        pluginEntryConfig: {
          BACKEND_API_URL:
            api?.config?.plugins?.entries?.["backend-jobs"]?.config?.BACKEND_API_URL ?? null,
          CLAWDBOT_SERVICE_TOKEN:
            api?.config?.plugins?.entries?.["backend-jobs"]?.config?.CLAWDBOT_SERVICE_TOKEN
              ? "[REDACTED]"
              : null,
        },
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(snapshot, null, 2)
          }
        ],
        structuredContent: snapshot
      };
    }
  });
}
