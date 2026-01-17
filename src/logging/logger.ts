export type LogLevel = "info" | "warn" | "error";

export interface LogMeta {
  requestId?: string;
  userId?: number;
  username?: string;
  service?: string;
  status?: string;
}

export class Logger {
  info(message: string, meta: LogMeta = {}): void {
    this.write("info", message, meta);
  }

  warn(message: string, meta: LogMeta = {}): void {
    this.write("warn", message, meta);
  }

  error(message: string, meta: LogMeta = {}): void {
    this.write("error", message, meta);
  }

  private write(level: LogLevel, message: string, meta: LogMeta): void {
    const timestamp = new Date().toISOString();
    const parts: string[] = [`time=${timestamp}`, `level=${level}`];

    if (meta.requestId) {
      parts.push(`request_id=${meta.requestId}`);
    }
    if (meta.userId !== undefined) {
      parts.push(`user_id=${meta.userId}`);
    }
    if (meta.username) {
      parts.push(`username=${meta.username}`);
    }
    if (meta.service) {
      parts.push(`service=${meta.service}`);
    }
    if (meta.status) {
      parts.push(`status=${meta.status}`);
    }

    parts.push(`msg="${sanitizeMessage(message)}"`);
    console.log(parts.join(" "));
  }
}

function sanitizeMessage(message: string): string {
  return message.replace(/"/g, "'");
}
