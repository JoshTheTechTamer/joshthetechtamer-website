import { handleClientPreviewsGate, isGatedDemoPath } from '../_lib/client-previews-gate.js';

export async function onRequest(context) {
  const path = new URL(context.request.url).pathname;
  if (!isGatedDemoPath(path)) {
    return context.next();
  }
  return handleClientPreviewsGate(context);
}
