import type { AppConfig } from "../config/env";
import type { Logger } from "../logging/logger";
import { MockTtsClient } from "./mock";
import { SaluteTtsClient } from "./salute";
import type { TtsClient } from "./types";

export function createTtsClient(config: AppConfig, logger: Logger): TtsClient {
  if (config.ttsProvider === "mock") {
    return new MockTtsClient();
  }
  if (config.ttsProvider === "salute") {
    return new SaluteTtsClient(config.salute, logger);
  }
  logger.warn(`Unsupported TTS provider: ${config.ttsProvider}`);
  return new MockTtsClient();
}
