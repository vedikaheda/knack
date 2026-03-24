import { registerCreateProofDocumentTool } from "./tools/createProofDocument";
import { registerFetchFirefliesTranscriptTool } from "./tools/fetchFirefliesTranscript";

export default function registerPlugin(api: any) {
  registerFetchFirefliesTranscriptTool(api);
  registerCreateProofDocumentTool(api);
}
