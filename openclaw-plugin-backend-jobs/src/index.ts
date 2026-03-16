import { registerCreateBrdFromTranscriptTool } from "./tools/createBrdFromTranscript";
import { registerGenerateReviewsTool } from "./tools/generateReviews";
import { registerRegenerateBrdTool } from "./tools/regenerateBrd";

export default function registerPlugin(api: any) {
  registerCreateBrdFromTranscriptTool(api);
  registerGenerateReviewsTool(api);
  registerRegenerateBrdTool(api);
}
