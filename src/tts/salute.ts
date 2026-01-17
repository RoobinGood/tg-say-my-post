import axios from "axios";
import { randomUUID } from "crypto";
import { promises as fs } from "fs";
import https from "https";
import path from "path";
import type { SaluteConfig } from "../config/env";
import type { Logger } from "../logging/logger";
import type { TtsClient } from "./types";

interface SaluteTokenResponse {
  access_token?: string;
  expires_at?: number;
  expires_in?: number;
}

export class SaluteTtsClient implements TtsClient {
  private accessToken: string | null = null;
  private tokenExpiresAt: number | null = null;
  private readonly httpsAgent = new https.Agent({ rejectUnauthorized: false });

  constructor(
    private readonly config: SaluteConfig,
    private readonly logger: Logger,
  ) {}

  async synthesize(
    text: string,
    requestId: string,
    chatId: number,
    messageId: number,
  ): Promise<string> {
    const token = await this.ensureToken(requestId);
    const tmpDir = path.resolve(this.config.tmpDir);
    await fs.mkdir(tmpDir, { recursive: true });

    const fileName = `${chatId}_${messageId}.${getFileExtFromFormat(this.config.format)}`;
    const filePath = path.join(tmpDir, fileName);
    const response = await this.requestSynthesis(token, text, requestId);
    const audioData = new Uint8Array(response.data);
    await fs.writeFile(filePath, audioData);
    return filePath;
  }

  private async ensureToken(requestId: string): Promise<string> {
    if (this.accessToken && this.tokenExpiresAt && !this.isTokenExpiringSoon()) {
      return this.accessToken;
    }

    const tokenResponse = await this.requestToken(requestId);
    if (!tokenResponse.access_token) {
      throw new Error("SaluteSpeech token response missing access_token.");
    }

    this.accessToken = tokenResponse.access_token;
    this.tokenExpiresAt = this.resolveTokenExpiry(tokenResponse);
    return this.accessToken;
  }

  private isTokenExpiringSoon(): boolean {
    if (!this.tokenExpiresAt) {
      return true;
    }
    const now = Date.now();
    return this.tokenExpiresAt - now <= this.config.tokenRefreshMarginMs;
  }

  private resolveTokenExpiry(response: SaluteTokenResponse): number {
    if (typeof response.expires_at === "number") {
      return response.expires_at;
    }
    if (typeof response.expires_in === "number") {
      return Date.now() + response.expires_in * 1000;
    }
    return Date.now() + 25 * 60 * 1000;
  }

  private async requestToken(requestId: string): Promise<SaluteTokenResponse> {
    const headers = {
      Authorization: `Basic ${this.config.authKey}`,
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/json",
      RqUID: randomUUID(),
    };

    const data = new URLSearchParams({ scope: this.config.scope });

    try {
      this.logger.info(
        `SaluteSpeech token request: ${serializeLogPayload({
          url: this.config.tokenUrl,
          scope: this.config.scope,
          headers: redactHeaders(headers),
        })}`,
        { requestId, service: "salute" },
      );
      const response = await axios.post(this.config.tokenUrl, data, {
        headers,
        httpsAgent: this.httpsAgent,
        timeout: this.config.timeoutMs,
      });
      return response.data as SaluteTokenResponse;
    } catch (error) {
      this.logger.error(
        `SaluteSpeech token request failed: ${describeAxiosError(error)}`,
        { requestId, service: "salute", status: "error" },
      );
      throw error;
    }
  }

  private async requestSynthesis(token: string, text: string, requestId: string) {
    const contentType = getContentType(this.config.useSsml);
    const headers = {
      Authorization: `Bearer ${token}`,
      "Content-Type": contentType,
    };

    try {
      this.logger.info(
        `SaluteSpeech synthesis request: ${serializeLogPayload({
          url: this.config.synthUrl,
          params: { format: this.config.format, voice: this.config.voice },
          contentType,
          textLength: text.length,
          headers: redactHeaders(headers),
        })}`,
        { requestId, service: "salute" },
      );
      return await axios.post(this.config.synthUrl, text, {
        headers,
        params: {
          format: this.config.format,
          voice: this.config.voice,
        },
        responseType: "arraybuffer",
        httpsAgent: this.httpsAgent,
        timeout: this.config.timeoutMs,
      });
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        this.logger.warn(
          `SaluteSpeech synthesis unauthorized, refreshing token: ${describeAxiosError(error)}`,
          { requestId, service: "salute", status: "error" },
        );
        this.accessToken = null;
        this.tokenExpiresAt = null;
        const refreshedToken = await this.ensureToken(requestId);
        return await axios.post(this.config.synthUrl, text, {
          headers: {
            Authorization: `Bearer ${refreshedToken}`,
            "Content-Type": contentType,
          },
          params: {
            format: this.config.format,
            voice: this.config.voice,
          },
          responseType: "arraybuffer",
          httpsAgent: this.httpsAgent,
          timeout: this.config.timeoutMs,
        });
      }

      this.logger.error(
        `SaluteSpeech synthesis request failed: ${describeAxiosError(error)}`,
        { requestId, service: "salute", status: "error" },
      );
      throw error;
    }
  }
}

function redactHeaders(headers: Record<string, string>): Record<string, string> {
  const redacted: Record<string, string> = {};
  for (const [key, value] of Object.entries(headers)) {
    if (key.toLowerCase() === "authorization") {
      redacted[key] = "<redacted>";
    } else {
      redacted[key] = value;
    }
  }
  return redacted;
}

function getContentType(useSsml: boolean): string {
  return useSsml ? "application/ssml" : "application/text";
}

function getFileExtFromFormat(format: string): string {
  const normalized = format.toLowerCase();
  if (normalized.startsWith("wav")) {
    return "wav";
  }
  if (normalized.startsWith("opus")) {
    return "opus";
  }
  if (normalized.startsWith("pcm")) {
    return "pcm";
  }
  return normalized;
}

function describeAxiosError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return String(error);
  }

  const details = {
    message: error.message,
    method: error.config?.method,
    url: error.config?.url,
    params: error.config?.params,
    status: error.response?.status,
    statusText: error.response?.statusText,
    responseData: formatResponseData(error.response?.data),
    responseHeaders: error.response?.headers,
  };

  return serializeLogPayload(details);
}

function formatResponseData(data: unknown): string | null {
  if (data === undefined || data === null) {
    return null;
  }
  if (typeof data === "string") {
    return truncate(data);
  }
  if (Buffer.isBuffer(data)) {
    return truncate(data.toString("utf8"));
  }
  if (data instanceof ArrayBuffer) {
    return truncate(Buffer.from(data).toString("utf8"));
  }
  if (ArrayBuffer.isView(data)) {
    return truncate(Buffer.from(data.buffer).toString("utf8"));
  }
  try {
    return truncate(JSON.stringify(data));
  } catch {
    return "<unserializable>";
  }
}

function serializeLogPayload(payload: unknown): string {
  try {
    return truncate(JSON.stringify(payload));
  } catch {
    return "<unserializable>";
  }
}

function truncate(value: string, maxLength = 2000): string {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength)}...<truncated>`;
}
