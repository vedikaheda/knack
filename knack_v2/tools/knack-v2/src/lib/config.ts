type PluginConfig = {
  FIREFLIES_API_KEY?: string;
  PROOF_BASE_URL?: string;
  PROOF_PUBLIC_URL?: string;
  PROOF_OWNER_SECRET_STORE_PATH?: string;
  KNACK_AUDIT_LOG_PATH?: string;
};

function getPluginConfig(api: any): PluginConfig {
  return (
    api?.plugin?.config ??
    api?.config?.plugins?.entries?.["knack-v2"]?.config ??
    api?.config ??
    {}
  );
}

export function requireConfig(api: any, key: keyof PluginConfig): string {
  const config = getPluginConfig(api);
  const value = config[key];

  if (!value || !String(value).trim()) {
    throw new Error(`Missing required plugin config: ${key}`);
  }

  return String(value).trim();
}

export function getConfig(api: any, key: keyof PluginConfig, fallback?: string): string | undefined {
  const config = getPluginConfig(api);
  const value = config[key];

  if (value === undefined || value === null || String(value).trim() === "") {
    return fallback;
  }

  return String(value).trim();
}
