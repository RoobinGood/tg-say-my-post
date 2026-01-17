import dotenv from "dotenv";

export type TtsProvider = "mock" | "salute";

export interface SaluteConfig {
  authKey: string;
  scope: string;
  tokenUrl: string;
  synthUrl: string;
  voice: string;
  format: string;
  useSsml: boolean;
  tmpDir: string;
  timeoutMs: number;
  tokenRefreshMarginMs: number;
}

export interface AppConfig {
  botToken: string;
  allowedUserIds: Set<number>;
  preprocessingEnabled: boolean;
  ttsProvider: TtsProvider;
  salute: SaluteConfig;
}

export function loadConfig(): AppConfig {
  dotenv.config();

  const botToken = readRequiredEnv("BOT_TOKEN");
  const allowedUserIds = parseAllowedUserIds(readRequiredEnv("ALLOWED_USER_IDS"));
  const preprocessingEnabled = readOptionalBooleanEnv("PREPROCESSING_ENABLED", false);
  const ttsProvider = readOptionalEnv("TTS_PROVIDER", "mock") as TtsProvider;
  const salute = loadSaluteConfig(ttsProvider);

  return {
    botToken,
    allowedUserIds,
    preprocessingEnabled,
    ttsProvider,
    salute,
  };
}

function readRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required env var: ${key}`);
  }
  return value;
}

function readOptionalEnv(key: string, fallback: string): string {
  const value = process.env[key];
  return value && value.length > 0 ? value : fallback;
}

function readOptionalNumberEnv(key: string, fallback: number): number {
  const value = process.env[key];
  if (!value) {
    return fallback;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function readOptionalBooleanEnv(key: string, fallback: boolean): boolean {
  const value = process.env[key];
  if (!value) {
    return fallback;
  }
  return value.toLowerCase() === "true" || value === "1";
}

function parseAllowedUserIds(rawValue: string): Set<number> {
  const ids = rawValue
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
    .map((item) => Number(item))
    .filter((item) => Number.isInteger(item));

  return new Set(ids);
}

function loadSaluteConfig(provider: TtsProvider): SaluteConfig {
  const useSsml = readOptionalBooleanEnv("SALUTE_USE_SSML", false);

  return {
    authKey:
      provider === "salute" ? readRequiredEnv("SALUTE_AUTH_KEY") : readOptionalEnv("SALUTE_AUTH_KEY", ""),
    scope: readOptionalEnv("SALUTE_SCOPE", "SALUTE_SPEECH_PERS"),
    tokenUrl: readOptionalEnv("SALUTE_TOKEN_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"),
    synthUrl: readOptionalEnv("SALUTE_SYNTH_URL", "https://smartspeech.sber.ru/rest/v1/text:synthesize"),
    voice: readOptionalEnv("SALUTE_VOICE", "Nec_24000"),
    format: readOptionalEnv("SALUTE_FORMAT", "wav16"),
    useSsml,
    tmpDir: readOptionalEnv("SALUTE_TMP_DIR", "tmp"),
    timeoutMs: readOptionalNumberEnv("SALUTE_TIMEOUT_MS", 30000),
    tokenRefreshMarginMs: readOptionalNumberEnv("SALUTE_TOKEN_REFRESH_MARGIN_MS", 60000),
  };
}
