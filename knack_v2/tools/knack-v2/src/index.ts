import { registerAckProofEventsTool } from "./tools/ackProofEvents";
import { registerApplyProofEditTool } from "./tools/applyProofEdit";
import { registerApplyProofOpsTool } from "./tools/applyProofOps";
import { registerCreateProofDocumentTool } from "./tools/createProofDocument";
import { registerFetchFirefliesTranscriptTool } from "./tools/fetchFirefliesTranscript";
import { registerGetProofDocumentStateTool } from "./tools/getProofDocumentState";
import { registerGetProofPendingEventsTool } from "./tools/getProofPendingEvents";

export default function registerPlugin(api: any) {
  registerFetchFirefliesTranscriptTool(api);
  registerCreateProofDocumentTool(api);
  registerGetProofDocumentStateTool(api);
  registerGetProofPendingEventsTool(api);
  registerApplyProofEditTool(api);
  registerApplyProofOpsTool(api);
  registerAckProofEventsTool(api);
}
