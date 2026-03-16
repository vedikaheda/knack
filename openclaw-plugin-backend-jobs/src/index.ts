import { registerCreateBrdFromTranscriptTool } from "./tools/createBrdFromTranscript";
import { registerRegenerateBrdTool } from "./tools/regenerateBrd";

export default function registerPlugin(api: any) {
  registerCreateBrdFromTranscriptTool(api);
  registerRegenerateBrdTool(api);
}
