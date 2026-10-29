import { WebWorkerMLCEngineHandler } from 'https://esm.sh/@mlc-ai/web-llm@0.2.86';
const handler = new WebWorkerMLCEngineHandler();
self.onmessage = message => handler.onmessage(message);
