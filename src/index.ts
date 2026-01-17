import { Bot, Context, InputFile } from "grammy";
import { randomUUID } from "crypto";
import { promises as fs } from "fs";
import { loadConfig } from "./config/env";
import { Logger } from "./logging/logger";
import { UnsupportedMessageError } from "./extractors/errors";
import { extractTextFromMessage } from "./extractors";
import { preprocessText } from "./preprocessing";
import { createTtsClient } from "./tts/factory";

interface RequestState {
  requestId: string;
}

type BotContext = Context & { state: RequestState };

const config = loadConfig();
const logger = new Logger();
const ttsClient = createTtsClient(config, logger);

const bot = new Bot<BotContext>(config.botToken);

bot.use(async (ctx, next) => {
  ctx.state = ctx.state ?? ({} as RequestState);
  ctx.state.requestId = randomUUID();
  await next();
});

bot.use(async (ctx, next) => {
  const userId = ctx.from?.id;
  if (!userId || !config.allowedUserIds.has(userId)) {
    return;
  }
  await next();
});

bot.command("start", async (ctx) => {
  logger.info("start command", {
    requestId: ctx.state.requestId,
    userId: ctx.from?.id,
    username: ctx.from?.username,
  });

  await ctx.reply(
    "Пришлите текст или репост сообщения/поста — я отвечу голосовым сообщением.",
  );
});

bot.on("message", async (ctx) => {
  const requestId = ctx.state.requestId;

  logger.info("message received", {
    requestId,
    userId: ctx.from?.id,
    username: ctx.from?.username,
  });

  try {
    const text = extractTextFromMessage(ctx.message);
    const processedText = config.preprocessingEnabled ? preprocessText(text) : text;
    const chatId = ctx.chat?.id;
    const messageId = ctx.message.message_id;

    if (!chatId) {
      throw new Error("Missing chat id.");
    }

    const audioPath = await ttsClient.synthesize(processedText, requestId, chatId, messageId);

    try {
      await ctx.replyWithVoice(new InputFile(audioPath), {
        reply_parameters: { message_id: messageId },
      });
    } finally {
      await fs.unlink(audioPath).catch(() => undefined);
    }
  } catch (error) {
    if (error instanceof UnsupportedMessageError) {
      await ctx.reply(
        "Пожалуйста, отправьте текст или репост поддерживаемого сообщения.",
        { reply_parameters: { message_id: ctx.message.message_id } },
      );
      return;
    }

    const message = error instanceof Error ? error.message : "Неизвестная ошибка.";
    await ctx.reply(message, {
      reply_parameters: { message_id: ctx.message.message_id },
    });
  }
});

bot.catch(async (error) => {
  logger.error("bot error: " + error.message, { status: "error" });

  if (error.ctx?.message) {
    const replyText = "Произошла ошибка. Пожалуйста, попробуйте еще раз.";
    await error.ctx.reply(replyText, {
      reply_parameters: { message_id: error.ctx.message.message_id },
    });
  }
});

async function startBot(): Promise<void> {
  logger.info("bot starting");
  await bot.start({
    onStart: (info) => {
      logger.info("bot started", { username: info.username });
    },
  });
}

startBot().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown error";
  logger.error("bot failed to start: " + message, { status: "error" });
  process.exit(1);
});
