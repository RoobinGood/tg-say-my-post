import type { Message } from "grammy/types";
import { UnsupportedMessageError } from "./errors";

interface ForwardOriginChannel {
  type: "channel";
  chat?: {
    title?: string;
    username?: string;
  };
}

interface ForwardOriginUser {
  type: "user";
  sender_user?: {
    username?: string;
    first_name?: string;
    last_name?: string;
  };
}

type MessageWithForward = Message & {
  forward_origin?: ForwardOriginChannel | ForwardOriginUser;
  forward_from_chat?: {
    type?: string;
    title?: string;
    username?: string;
  };
  forward_from?: {
    username?: string;
    first_name?: string;
    last_name?: string;
  };
  forward_sender_name?: string;
};

export function extractTextFromMessage(message: Message): string {
  const withForward = message as MessageWithForward;
  const text = message.text ?? message.caption;

  if (!text || text.trim().length === 0) {
    throw new UnsupportedMessageError(
      "Пожалуйста, отправьте текст или репост поддерживаемого сообщения.",
    );
  }

  const channelName = getForwardedChannelName(withForward);
  if (channelName !== null) {
    const prefix = channelName.length > 0 ? `Пост из канала ${channelName}.` : "Пост из канала.";
    return `${prefix}\n\n${text}`;
  }

  const userName = getForwardedUserName(withForward);
  if (userName !== null) {
    const prefix =
      userName.length > 0 ? `Сообщение от пользователя ${userName}.` : "Сообщение от пользователя.";
    return `${prefix}\n\n${text}`;
  }

  return text;
}

function getForwardedChannelName(message: MessageWithForward): string | null {
  if (message.forward_origin?.type === "channel") {
    return message.forward_origin.chat?.title || message.forward_origin.chat?.username || "";
  }

  if (message.forward_from_chat && message.forward_from_chat.type === "channel") {
    return message.forward_from_chat.title || message.forward_from_chat.username || "";
  }

  return null;
}

function getForwardedUserName(message: MessageWithForward): string | null {
  if (message.forward_origin?.type === "user") {
    return buildUserName(
      message.forward_origin.sender_user?.username,
      message.forward_origin.sender_user?.first_name,
      message.forward_origin.sender_user?.last_name,
      undefined,
    );
  }

  if (message.forward_from || message.forward_sender_name) {
    return buildUserName(
      message.forward_from?.username,
      message.forward_from?.first_name,
      message.forward_from?.last_name,
      message.forward_sender_name,
    );
  }

  return null;
}

function buildUserName(
  username?: string,
  firstName?: string,
  lastName?: string,
  fallbackName?: string,
): string {
  if (username && username.length > 0) {
    return `@${username}`;
  }

  const fullName = [firstName, lastName].filter(Boolean).join(" ").trim();
  if (fullName.length > 0) {
    return fullName;
  }

  return fallbackName || "";
}
