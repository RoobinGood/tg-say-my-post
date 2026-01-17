import { TtsClient } from "./types";

export class MockTtsClient implements TtsClient {
  async synthesize(
    _text: string,
    _requestId: string,
    _chatId: number,
    _messageId: number,
  ): Promise<string> {
    throw new Error("Озвучка еще не настроена.");
  }
}
