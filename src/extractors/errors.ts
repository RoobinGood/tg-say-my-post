export class UnsupportedMessageError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UnsupportedMessageError";
  }
}
