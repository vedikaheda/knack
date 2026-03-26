import { registerProofRoutingHook } from "./hooks/proofRouting";
import { registerAckProofEventsTool } from "./tools/ackProofEvents";
import { registerApplyProofEditTool } from "./tools/applyProofEdit";
import { registerApplyProofEditV2Tool } from "./tools/applyProofEditV2";
import { registerApplyProofOpsTool } from "./tools/applyProofOps";
import { registerCreateProofDocumentTool } from "./tools/createProofDocument";
import { registerFetchFirefliesTranscriptTool } from "./tools/fetchFirefliesTranscript";
import { registerGetProofDocumentStateTool } from "./tools/getProofDocumentState";
import { registerGetProofPendingEventsTool } from "./tools/getProofPendingEvents";
import { registerGetProofSnapshotTool } from "./tools/getProofSnapshot";

export default function registerPlugin(api: any) {
  registerProofRoutingHook(api);
  registerFetchFirefliesTranscriptTool(api);
  registerCreateProofDocumentTool(api);
  registerGetProofDocumentStateTool(api);
  registerGetProofSnapshotTool(api);
  registerGetProofPendingEventsTool(api);
  registerApplyProofEditTool(api);
  registerApplyProofEditV2Tool(api);
  registerApplyProofOpsTool(api);
  registerAckProofEventsTool(api);
}
