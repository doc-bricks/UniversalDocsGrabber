import test from "node:test";
import assert from "node:assert/strict";

import {
  filterDocuments,
  getDemoLibrary,
  normalizeLibraryPayload,
  parseLibraryText
} from "../library.js";

test("normalizeLibraryPayload accepts minimal valid export", () => {
  const payload = normalizeLibraryPayload({
    schema: "docsgrabber-library",
    schema_version: "1.0",
    documents: [
      {
        profile_name: "Rechnungen",
        filename: "beleg.pdf",
        path_hint: {
          kind: "basename",
          value: "beleg.pdf"
        }
      }
    ]
  });

  assert.equal(payload.summary.document_count, 1);
  assert.equal(payload.documents[0].filename, "beleg.pdf");
  assert.equal(payload.documents[0].category, "Ohne Kategorie");
});

test("parseLibraryText rejects unsupported schema versions", () => {
  assert.throws(
    () => parseLibraryText(JSON.stringify({ schema: "docsgrabber-library", schema_version: "2.0" })),
    /Nicht unterstützte Schema-Version/
  );
});

test("filterDocuments applies query and status filters", () => {
  const payload = getDemoLibrary();
  const filtered = filterDocuments(payload.documents, {
    query: "mahnung",
    status: "missing"
  });

  assert.equal(filtered.length, 1);
  assert.equal(filtered[0].filename, "mahnung.png");
});

test("getDemoLibrary exposes stable summary counts", () => {
  const payload = getDemoLibrary();

  assert.equal(payload.summary.profile_count, 2);
  assert.equal(payload.summary.document_count, 3);
  assert.equal(payload.summary.missing_count, 1);
});
