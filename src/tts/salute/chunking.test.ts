import { test } from "node:test";
import assert from "node:assert";
import { splitTextForSalute } from "./chunking";

const MAX_CHUNK_SIZE = 4000;

function generateText(length: number, char: string = "a"): string {
  return char.repeat(length);
}

function generateParagraph(length: number): string {
  return generateText(length);
}

function generateSentence(length: number): string {
  return generateText(length - 1) + ".";
}

test("splitTextForSalute: текст меньше лимита возвращается как один чанк", () => {
  const text = generateText(100);
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 1);
  assert.strictEqual(result[0], text);
});

test("splitTextForSalute: текст равен лимиту возвращается как один чанк", () => {
  const text = generateText(MAX_CHUNK_SIZE);
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 1);
  assert.strictEqual(result[0], text);
});

test("splitTextForSalute: несколько маленьких абзацев объединяются в один чанк", () => {
  const paragraph1 = generateParagraph(500);
  const paragraph2 = generateParagraph(500);
  const paragraph3 = generateParagraph(500);
  const text = `${paragraph1}\n\n${paragraph2}\n\n${paragraph3}`;
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 1);
  assert(result[0].includes(paragraph1));
  assert(result[0].includes(paragraph2));
  assert(result[0].includes(paragraph3));
});

test("splitTextForSalute: абзацы объединяются до лимита", () => {
  const paragraph1 = generateParagraph(1500);
  const paragraph2 = generateParagraph(1500);
  const paragraph3 = generateParagraph(996);
  const text = `${paragraph1}\n\n${paragraph2}\n\n${paragraph3}`;
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 1);
  assert.strictEqual(result[0].length, paragraph1.length + paragraph2.length + paragraph3.length + 4);
});

test("splitTextForSalute: когда объединенные абзацы превышают лимит, они разделяются", () => {
  const paragraph1 = generateParagraph(2500);
  const paragraph2 = generateParagraph(2500);
  const text = `${paragraph1}\n\n${paragraph2}`;
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 2);
  assert.strictEqual(result[0], paragraph1);
  assert.strictEqual(result[1], paragraph2);
});

test("splitTextForSalute: большой абзац разбивается по предложениям", () => {
  const sentence1 = generateSentence(500);
  const sentence2 = generateSentence(500);
  const sentence3 = generateSentence(500);
  const sentence4 = generateSentence(500);
  const sentence5 = generateSentence(500);
  const sentence6 = generateSentence(500);
  const sentence7 = generateSentence(500);
  const sentence8 = generateSentence(500);
  const sentence9 = generateSentence(500);
  const paragraph = `${sentence1} ${sentence2} ${sentence3} ${sentence4} ${sentence5} ${sentence6} ${sentence7} ${sentence8} ${sentence9}`;
  const result = splitTextForSalute(paragraph);
  assert(result.length > 1);
  for (const chunk of result) {
    assert(chunk.length <= MAX_CHUNK_SIZE);
  }
});

test("splitTextForSalute: предложение больше лимита разбивается принудительно", () => {
  const longSentence = generateText(5000);
  const result = splitTextForSalute(longSentence);
  assert(result.length > 1);
  for (const chunk of result) {
    assert(chunk.length <= MAX_CHUNK_SIZE);
  }
});

test("splitTextForSalute: смешанный случай - маленькие и большие абзацы", () => {
  const small1 = generateParagraph(500);
  const small2 = generateParagraph(500);
  const large = generateParagraph(5000);
  const small3 = generateParagraph(1000);
  const text = `${small1}\n\n${small2}\n\n${large}\n\n${small3}`;
  const result = splitTextForSalute(text);
  assert(result.length >= 3);
  const firstChunk = result[0];
  assert(firstChunk.includes(small1));
  assert(firstChunk.includes(small2));
  assert(firstChunk.length <= MAX_CHUNK_SIZE);
  for (const chunk of result) {
    assert(chunk.length <= MAX_CHUNK_SIZE);
  }
});

test("splitTextForSalute: пустые абзацы игнорируются", () => {
  const paragraph1 = generateParagraph(500);
  const paragraph2 = generateParagraph(500);
  const text = `${paragraph1}\n\n\n\n${paragraph2}`;
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 1);
  assert(result[0].includes(paragraph1));
  assert(result[0].includes(paragraph2));
});

test("splitTextForSalute: все чанки не превышают лимит", () => {
  const paragraphs: string[] = [];
  for (let i = 0; i < 20; i++) {
    paragraphs.push(generateParagraph(300));
  }
  const text = paragraphs.join("\n\n");
  const result = splitTextForSalute(text);
  for (const chunk of result) {
    assert(chunk.length <= MAX_CHUNK_SIZE, `Chunk length ${chunk.length} exceeds ${MAX_CHUNK_SIZE}`);
  }
});

test("splitTextForSalute: текст без абзацев разбивается по предложениям", () => {
  const sentence1 = generateSentence(2000);
  const sentence2 = generateSentence(2000);
  const sentence3 = generateSentence(2000);
  const text = `${sentence1} ${sentence2} ${sentence3}`;
  const result = splitTextForSalute(text);
  assert(result.length >= 2);
  for (const chunk of result) {
    assert(chunk.length <= MAX_CHUNK_SIZE);
  }
});

test("splitTextForSalute: очень длинный текст без разделителей разбивается корректно", () => {
  const text = generateText(10000);
  const result = splitTextForSalute(text);
  assert(result.length > 1);
  for (const chunk of result) {
    assert(chunk.length <= MAX_CHUNK_SIZE);
  }
  const reconstructed = result.join("");
  assert.strictEqual(reconstructed.length, text.length);
});

test("splitTextForSalute: граничный случай - абзац ровно на границе", () => {
  const paragraph1 = generateParagraph(MAX_CHUNK_SIZE - 3);
  const paragraph2 = generateParagraph(1);
  const text = `${paragraph1}\n\n${paragraph2}`;
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 1);
  assert.strictEqual(result[0].length, paragraph1.length + paragraph2.length + 2);
});

test("splitTextForSalute: граничный случай - абзац превышает на 1 символ", () => {
  const paragraph1 = generateParagraph(MAX_CHUNK_SIZE);
  const paragraph2 = generateParagraph(1);
  const text = `${paragraph1}\n\n${paragraph2}`;
  const result = splitTextForSalute(text);
  assert.strictEqual(result.length, 2);
});
