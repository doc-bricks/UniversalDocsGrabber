import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";

const dir = join(dirname(fileURLToPath(import.meta.url)), "..");
const appSrc = readFileSync(join(dir, "app.js"), "utf8");
const swSrc = readFileSync(join(dir, "sw.js"), "utf8");

// sw.js checks

test("sw.js: alle Manifest-Icons im ASSETS-Array", () => {
  assert.ok(swSrc.includes("./icons/Icon-192.png"), "Icon-192.png fehlt");
  assert.ok(swSrc.includes("./icons/Icon-512.png"), "Icon-512.png fehlt");
  assert.ok(swSrc.includes("./icons/Icon-maskable-192.png"), "Icon-maskable-192.png fehlt");
  assert.ok(swSrc.includes("./icons/Icon-maskable-512.png"), "Icon-maskable-512.png fehlt");
});

test("sw.js: caches.match mit ignoreSearch:true", () => {
  assert.ok(
    swSrc.includes("ignoreSearch: true"),
    "ignoreSearch: true fehlt in caches.match()"
  );
});

test("sw.js: self.skipWaiting() im install-Handler", () => {
  assert.ok(swSrc.includes("self.skipWaiting()"), "self.skipWaiting() fehlt");
});

test("sw.js: self.clients.claim() im activate-Handler", () => {
  assert.ok(swSrc.includes("self.clients.claim()"), "self.clients.claim() fehlt");
});

// app.js checks

test("app.js: escHtml-Funktion vorhanden", () => {
  assert.ok(appSrc.includes("function escHtml("), "escHtml fehlt in app.js");
});

test("app.js: renderDocuments nutzt 'doc' statt 'document' als forEach-Parameter", () => {
  assert.ok(
    !appSrc.includes("documents.forEach((document)"),
    "DOM-shadowing Bug: 'document' wird noch als forEach-Parameter genutzt"
  );
  assert.ok(appSrc.includes("documents.forEach((doc)"), "forEach-Parameter 'doc' fehlt");
});

test("app.js: renderDocuments verwendet document.createElement (DOM-Global unberührt)", () => {
  assert.ok(
    appSrc.includes('document.createElement("article")'),
    "document.createElement fehlt nach Bug-Fix"
  );
});

test("app.js: innerHTML-Interpolationen in renderDocuments verwenden escHtml", () => {
  const renderDocumentsBlock = appSrc.slice(appSrc.indexOf("function renderDocuments("));
  assert.ok(
    renderDocumentsBlock.includes("escHtml(doc.filename)"),
    "escHtml fehlt bei doc.filename"
  );
  assert.ok(
    renderDocumentsBlock.includes("escHtml(doc.profile_name)"),
    "escHtml fehlt bei doc.profile_name"
  );
});

test("app.js: innerHTML-Interpolationen in renderProfiles verwenden escHtml", () => {
  const block = appSrc.slice(appSrc.indexOf("function renderProfiles("));
  assert.ok(block.includes("escHtml(profile.name)"), "escHtml fehlt bei profile.name");
  assert.ok(block.includes("escHtml(profile.group)"), "escHtml fehlt bei profile.group");
});

test("app.js: innerHTML-Interpolationen in renderCategories verwenden escHtml", () => {
  const block = appSrc.slice(appSrc.indexOf("function renderCategories("));
  assert.ok(block.includes("escHtml(category.name)"), "escHtml fehlt bei category.name");
});

test("app.js: innerHTML-Interpolationen in renderDocumentDetail verwenden escHtml", () => {
  const block = appSrc.slice(appSrc.indexOf("function renderDocumentDetail("));
  assert.ok(block.includes("escHtml(document.filename)"), "escHtml fehlt bei document.filename");
  assert.ok(block.includes("escHtml(document.profile_name)"), "escHtml fehlt bei document.profile_name");
});

test("app.js: escHtml enkodiert Sonderzeichen korrekt (runtime)", () => {
  const match = appSrc.match(/function escHtml\([\s\S]*?\n\}/);
  assert.ok(match, "escHtml-Funktion konnte nicht aus app.js extrahiert werden");
  const escHtmlFn = new Function(`${match[0]}; return escHtml;`)();
  assert.equal(escHtmlFn("<img src=x onerror=alert(1)>"), "&lt;img src=x onerror=alert(1)&gt;");
  assert.equal(escHtmlFn("a & b"), "a &amp; b");
  assert.equal(escHtmlFn('"quoted"'), "&quot;quoted&quot;");
  assert.equal(escHtmlFn("safe text"), "safe text");
});
