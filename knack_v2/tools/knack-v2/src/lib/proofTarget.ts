import { ProofTarget, parseProofUrl } from "./proof";

export function resolveProofTargetInput(input: {
  slug?: string;
  token?: string;
  proofUrl?: string;
}): ProofTarget {
  if (input.proofUrl) {
    return parseProofUrl(input.proofUrl);
  }

  if (!input.slug || !input.token) {
    throw new Error("Provide either proofUrl or both slug and token");
  }

  return {
    slug: input.slug,
    token: input.token,
  };
}
