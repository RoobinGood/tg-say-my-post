import { test } from "node:test";
import assert from "node:assert";
import type { Message } from "grammy/types";
import { extractTextFromMessage } from "./index";
import { UnsupportedMessageError } from "./errors";

function createMessage(text?: string, caption?: string): Message {
  return {
    message_id: 1,
    date: Date.now(),
    chat: { id: 1, type: "private", first_name: "Test" },
    text,
    caption,
  } as unknown as Message;
}

function createForwardedChannelMessage(
  text: string,
  channelTitle?: string,
  channelUsername?: string,
): Message {
  return {
    message_id: 1,
    date: Date.now(),
    chat: { id: 1, type: "private", first_name: "Test" },
    text,
    forward_origin: {
      type: "channel",
      chat: {
        title: channelTitle,
        username: channelUsername,
      },
    },
  } as unknown as Message;
}

function createForwardedChannelMessageLegacy(
  text: string,
  channelTitle?: string,
  channelUsername?: string,
): Message {
  return {
    message_id: 1,
    date: Date.now(),
    chat: { id: 1, type: "private", first_name: "Test" },
    text,
    forward_from_chat: {
      type: "channel",
      title: channelTitle,
      username: channelUsername,
    },
  } as unknown as Message;
}

function createForwardedUserMessage(
  text: string,
  username?: string,
  firstName?: string,
  lastName?: string,
): Message {
  return {
    message_id: 1,
    date: Date.now(),
    chat: { id: 1, type: "private", first_name: "Test" },
    text,
    forward_origin: {
      type: "user",
      sender_user: {
        username,
        first_name: firstName,
        last_name: lastName,
      },
    },
  } as unknown as Message;
}

function createForwardedUserMessageLegacy(
  text: string,
  username?: string,
  firstName?: string,
  lastName?: string,
  senderName?: string,
): Message {
  return {
    message_id: 1,
    date: Date.now(),
    chat: { id: 1, type: "private", first_name: "Test" },
    text,
    forward_from: {
      username,
      first_name: firstName,
      last_name: lastName,
    },
    forward_sender_name: senderName,
  } as unknown as Message;
}

test("extractTextFromMessage: извлекает текст из обычного сообщения", () => {
  const message = createMessage("Привет как дела");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Привет как дела");
});

test("extractTextFromMessage: извлекает caption, если text отсутствует", () => {
  const message = createMessage(undefined, "Подпись к фото");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Подпись к фото");
});

test("extractTextFromMessage: предпочитает text над caption", () => {
  const message = createMessage("Текст сообщения", "Подпись к фото");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Текст сообщения");
});

test("extractTextFromMessage: выбрасывает UnsupportedMessageError для пустого текста", () => {
  const message = createMessage("");
  assert.throws(() => extractTextFromMessage(message), UnsupportedMessageError);
});

test("extractTextFromMessage: выбрасывает UnsupportedMessageError для текста только из пробелов", () => {
  const message = createMessage("   ");
  assert.throws(() => extractTextFromMessage(message), UnsupportedMessageError);
});

test("extractTextFromMessage: выбрасывает UnsupportedMessageError, если text и caption отсутствуют", () => {
  const message = createMessage();
  assert.throws(() => extractTextFromMessage(message), UnsupportedMessageError);
});

test("extractTextFromMessage: добавляет префикс для репоста канала с названием", () => {
  const message = createForwardedChannelMessage("Текст поста", "Название канала");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Пост из канала Название канала.\n\nТекст поста");
});

test("extractTextFromMessage: добавляет префикс для репоста канала с username", () => {
  const message = createForwardedChannelMessage("Текст поста", undefined, "channel_username");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Пост из канала channel_username.\n\nТекст поста");
});

test("extractTextFromMessage: предпочитает title над username для канала", () => {
  const message = createForwardedChannelMessage("Текст поста", "Название", "username");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Пост из канала Название.\n\nТекст поста");
});

test("extractTextFromMessage: добавляет префикс для репоста канала без названия", () => {
  const message = createForwardedChannelMessage("Текст поста");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Пост из канала.\n\nТекст поста");
});

test("extractTextFromMessage: обрабатывает legacy формат репоста канала", () => {
  const message = createForwardedChannelMessageLegacy("Текст поста", "Название канала");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Пост из канала Название канала.\n\nТекст поста");
});

test("extractTextFromMessage: добавляет префикс для репоста пользователя с username", () => {
  const message = createForwardedUserMessage("Текст сообщения", "username");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя @username.\n\nТекст сообщения");
});

test("extractTextFromMessage: добавляет префикс для репоста пользователя с именем", () => {
  const message = createForwardedUserMessage("Текст сообщения", undefined, "Иван", "Петров");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя Иван Петров.\n\nТекст сообщения");
});

test("extractTextFromMessage: предпочитает username над именем для пользователя", () => {
  const message = createForwardedUserMessage("Текст", "username", "Иван", "Петров");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя @username.\n\nТекст");
});

test("extractTextFromMessage: использует только firstName, если lastName отсутствует", () => {
  const message = createForwardedUserMessage("Текст", undefined, "Иван");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя Иван.\n\nТекст");
});

test("extractTextFromMessage: добавляет префикс для репоста пользователя без данных", () => {
  const message = createForwardedUserMessage("Текст сообщения");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя.\n\nТекст сообщения");
});

test("extractTextFromMessage: обрабатывает legacy формат репоста пользователя с username", () => {
  const message = createForwardedUserMessageLegacy("Текст", "username");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя @username.\n\nТекст");
});

test("extractTextFromMessage: обрабатывает legacy формат репоста пользователя с именем", () => {
  const message = createForwardedUserMessageLegacy("Текст", undefined, "Иван", "Петров");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя Иван Петров.\n\nТекст");
});

test("extractTextFromMessage: использует forward_sender_name как fallback в legacy формате", () => {
  const message = createForwardedUserMessageLegacy("Текст", undefined, undefined, undefined, "Имя отправителя");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя Имя отправителя.\n\nТекст");
});

test("extractTextFromMessage: предпочитает username над forward_sender_name в legacy формате", () => {
  const message = createForwardedUserMessageLegacy("Текст", "username", undefined, undefined, "Имя");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя @username.\n\nТекст");
});

test("extractTextFromMessage: предпочитает имя над forward_sender_name в legacy формате", () => {
  const message = createForwardedUserMessageLegacy("Текст", undefined, "Иван", "Петров", "Другое имя");
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Сообщение от пользователя Иван Петров.\n\nТекст");
});

test("extractTextFromMessage: предпочитает новый формат forward_origin над legacy", () => {
  const message = {
    message_id: 1,
    date: Date.now(),
    chat: { id: 1, type: "private", first_name: "Test" },
    text: "Текст",
    forward_origin: {
      type: "channel",
      chat: { title: "Новый формат" },
    },
    forward_from_chat: {
      type: "channel",
      title: "Legacy формат",
    },
  } as unknown as Message;
  const result = extractTextFromMessage(message);
  assert.strictEqual(result, "Пост из канала Новый формат.\n\nТекст");
});
