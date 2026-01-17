export interface TtsClient {
  synthesize(
    text: string,
    requestId: string,
    chatId: number,
    messageId: number,
  ): Promise<string>;
}
