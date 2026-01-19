import { test } from "node:test";
import assert from "node:assert";
import { preprocessText } from "./index";

test("preprocessText: удаляет эмодзи из текста", () => {
  const input = "Привет 😊 как дела 🎉";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет  как дела. ");
});

test("preprocessText: заменяет ведущий эмодзи на абзац", () => {
  const input = "😊 Привет как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "\n\n Привет как дела.");
});

test("preprocessText: заменяет ведущий эмодзи с пробелами на абзац", () => {
  const input = "  😊 Привет как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "  \n\n Привет как дела.");
});

test("preprocessText: капитализирует первую букву, если она строчная", () => {
  const input = "привет как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела.");
});

test("preprocessText: капитализирует первую букву после пробелов", () => {
  const input = "   привет как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "   Привет как дела.");
});

test("preprocessText: не меняет первую букву, если она уже заглавная", () => {
  const input = "Привет как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела.");
});

test("preprocessText: добавляет точку в конце, если её нет", () => {
  const input = "Привет как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела.");
});

test("preprocessText: не добавляет точку, если она уже есть", () => {
  const input = "Привет как дела.";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела.");
});

test("preprocessText: не добавляет точку, если текст заканчивается на знак препинания", () => {
  const input = "Привет как дела!";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела!");
});

test("preprocessText: не добавляет точку, если текст заканчивается на вопросительный знак", () => {
  const input = "Привет как дела?";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела?");
});

test("preprocessText: сохраняет пробелы в конце при добавлении точки", () => {
  const input = "Привет как дела   ";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет как дела.   ");
});

test("preprocessText: обрабатывает пустую строку", () => {
  const input = "";
  const result = preprocessText(input);
  assert.strictEqual(result, "");
});

test("preprocessText: обрабатывает строку только из пробелов", () => {
  const input = "   ";
  const result = preprocessText(input);
  assert.strictEqual(result, "   ");
});

test("preprocessText: обрабатывает строку только из эмодзи", () => {
  const input = "😊🎉👍";
  const result = preprocessText(input);
  assert.strictEqual(result, "\n\n");
});

test("preprocessText: комплексный тест - все преобразования вместе", () => {
  const input = "  😊 привет как дела 🎉";
  const result = preprocessText(input);
  assert.strictEqual(result, "  \n\n Привет как дела. ");
});

test("preprocessText: удаляет эмодзи модификаторы и соединители", () => {
  const input = "Привет 👨‍👩‍👧 как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет  как дела.");
});

test("preprocessText: обрабатывает текст с цифрами в конце", () => {
  const input = "Привет 123";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет 123.");
});

test("preprocessText: не добавляет точку после цифры, если текст заканчивается на цифру", () => {
  const input = "Привет 123.";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет 123.");
});

test("preprocessText: обрабатывает текст с несколькими эмодзи подряд", () => {
  const input = "Привет 😊🎉👍 как дела";
  const result = preprocessText(input);
  assert.strictEqual(result, "Привет  как дела.");
});
