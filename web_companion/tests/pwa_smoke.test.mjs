import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { execSync } from "node:child_process";
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

// ── iOS PWA-Härtung ──────────────────────────────────────────────────────────

const htmlSrc = readFileSync(join(dir, "index.html"), "utf8");
const cssSrc = readFileSync(join(dir, "app.css"), "utf8");

describe("index.html iOS-PWA-Meta", () => {
  test("viewport-Meta enthält viewport-fit=cover", () => {
    assert.match(htmlSrc, /<meta[^>]*name="viewport"[^>]*viewport-fit=cover/);
  });

  test("viewport-Meta enthält width=device-width und initial-scale=1", () => {
    assert.match(htmlSrc, /<meta[^>]*name="viewport"[^>]*width=device-width/);
    assert.match(htmlSrc, /<meta[^>]*name="viewport"[^>]*initial-scale=1/);
  });

  test("apple-mobile-web-app-title ist gesetzt", () => {
    assert.match(htmlSrc, /<meta[^>]*name="apple-mobile-web-app-title"[^>]*content="[^"]+"/)
  });

  test("apple-mobile-web-app-status-bar-style ist gesetzt", () => {
    assert.match(htmlSrc, /<meta[^>]*name="apple-mobile-web-app-status-bar-style"[^>]*content="[^"]+"/)
  });

  test("apple-touch-icon hat sizes=\"180x180\"", () => {
    assert.match(htmlSrc, /<link[^>]*rel="apple-touch-icon"[^>]*sizes="180x180"/);
  });

  test("apple-touch-icon verweist auf apple-touch-icon-180.png", () => {
    assert.match(htmlSrc, /<link[^>]*rel="apple-touch-icon"[^>]*href="[^"]*apple-touch-icon-180\.png"/);
  });

  test("KEIN apple-mobile-web-app-capable (deprecated seit iOS 11.3)", () => {
    assert.doesNotMatch(htmlSrc, /apple-mobile-web-app-capable/, "deprecated — darf nicht gesetzt sein");
  });

  test("keine doppelten viewport-Meta-Tags", () => {
    const matches = htmlSrc.match(/<meta[^>]*name="viewport"/g) ?? [];
    assert.equal(matches.length, 1, `Genau 1 viewport-Meta erwartet, gefunden: ${matches.length}`);
  });

  test("theme-color Meta-Tag ist gesetzt", () => {
    assert.match(htmlSrc, /<meta[^>]*name="theme-color"[^>]*content="[^"]+"/)
  });
});

describe("app.css safe-area-inset", () => {
  test("safe-area-inset-top in CSS", () => {
    assert.ok(cssSrc.includes("env(safe-area-inset-top"), "safe-area-inset-top fehlt in app.css");
  });

  test("safe-area-inset-bottom in CSS", () => {
    assert.ok(cssSrc.includes("env(safe-area-inset-bottom"), "safe-area-inset-bottom fehlt in app.css");
  });
});

describe("apple-touch-icon-180.png — opaques RGB", () => {
  const iconPath = join(dir, "icons", "apple-touch-icon-180.png");

  test("apple-touch-icon-180.png existiert", () => {
    assert.ok(existsSync(iconPath), "icons/apple-touch-icon-180.png fehlt");
  });

  test("apple-touch-icon-180.png ist opakes RGB (keine Transparenz)", () => {
    const p = iconPath.replace(/\\/g, "/");
    const result = execSync(
      `python -c "from PIL import Image; img=Image.open('${p}'); d=list(img.getdata()); t=sum(1 for px in d if len(px)==4 and px[3]==0); print(t)"`,
      { encoding: "utf8" }
    ).trim();
    assert.equal(result, "0", `apple-touch-icon-180.png hat transparente Pixel: ${result}`);
  });
});

describe("sw.js iOS-Härtung", () => {
  test("CACHE_NAME ist v2 oder höher", () => {
    assert.match(swSrc, /docsgrabber-companion-v[2-9]/, "CACHE_NAME muss v2+ sein");
  });

  test("apple-touch-icon-180.png ist in ASSETS gecacht", () => {
    assert.ok(swSrc.includes("apple-touch-icon-180.png"), "apple-touch-icon-180.png fehlt in ASSETS");
  });
});
