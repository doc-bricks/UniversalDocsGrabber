function asString(value, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function asBoolean(value, fallback = false) {
  return typeof value === "boolean" ? value : fallback;
}

function asNumber(value, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizePathHint(pathHint) {
  if (!pathHint || typeof pathHint !== "object" || Array.isArray(pathHint)) {
    return { kind: "unknown", value: "" };
  }

  return {
    kind: asString(pathHint.kind, "unknown"),
    value: asString(pathHint.value)
  };
}

function buildDocumentId(document, index) {
  const profile = asString(document?.profile_name, "profil").toLowerCase().replace(/[^a-z0-9]+/g, "-");
  const filename = asString(document?.filename, "datei").toLowerCase().replace(/[^a-z0-9]+/g, "-");
  return `${profile || "profil"}-${filename || "datei"}-${index + 1}`;
}

function normalizeDocument(document, index) {
  return {
    id: buildDocumentId(document, index),
    profile_name: asString(document?.profile_name, "Unbekanntes Profil"),
    filename: asString(document?.filename, `Dokument ${index + 1}`),
    document_date: asString(document?.document_date),
    file_type: asString(document?.file_type),
    category: asString(document?.category, "Ohne Kategorie"),
    path_hint: normalizePathHint(document?.path_hint),
    status: asString(document?.status, "unknown"),
    sha256: asString(document?.sha256)
  };
}

function normalizeProfile(profile) {
  const effectiveSettings = profile?.effective_settings && typeof profile.effective_settings === "object"
    ? profile.effective_settings
    : {};

  return {
    id: asString(profile?.id),
    name: asString(profile?.name, "Unbenanntes Profil"),
    group: asString(profile?.group, "Allgemein"),
    active: asBoolean(profile?.active, false),
    account_ref: asString(profile?.account_ref),
    target_folder: asString(profile?.target_folder),
    filters: {
      subject: asString(profile?.filters?.subject),
      sender: asString(profile?.filters?.sender),
      since: asString(profile?.filters?.since),
      gmail_query: asString(profile?.filters?.gmail_query)
    },
    effective_settings: {
      download_attachments: asBoolean(effectiveSettings.download_attachments, true),
      convert_body_to_pdf: asBoolean(effectiveSettings.convert_body_to_pdf, false),
      convert_all_to_pdf: asBoolean(effectiveSettings.convert_all_to_pdf, false),
      enable_hash_check: asBoolean(effectiveSettings.enable_hash_check, false),
      auto_categorize: asBoolean(effectiveSettings.auto_categorize, false),
      category_rule_count: asNumber(effectiveSettings.category_rule_count, 0),
      formats: asArray(effectiveSettings.formats).map((entry) => asString(entry)).filter(Boolean)
    },
    document_count: asNumber(profile?.document_count, 0),
    last_document_date: asString(profile?.last_document_date)
  };
}

function normalizeCategory(category) {
  return {
    name: asString(category?.name, "Ohne Namen"),
    source: asString(category?.source, "unknown"),
    rule_count: asNumber(category?.rule_count, 0),
    document_count: asNumber(category?.document_count, 0)
  };
}

function normalizeAccount(account) {
  return {
    ref: asString(account?.ref),
    profile_count: asNumber(account?.profile_count, 0)
  };
}

function normalizeProfileStat(entry) {
  return {
    profile_name: asString(entry?.profile_name, "Unbekannt"),
    document_count: asNumber(entry?.document_count, 0),
    last_document_date: asString(entry?.last_document_date),
    active: asBoolean(entry?.active, false)
  };
}

export function normalizeLibraryPayload(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Der Export muss ein JSON-Objekt sein.");
  }

  const schema = asString(payload.schema);
  if (schema !== "docsgrabber-library") {
    throw new Error(`Nicht unterstütztes Schema: ${schema || "leer"}`);
  }

  const schemaVersion = asString(payload.schema_version);
  if (!schemaVersion.startsWith("1.")) {
    throw new Error(`Nicht unterstützte Schema-Version: ${schemaVersion || "leer"}`);
  }

  const profiles = asArray(payload.profiles).map(normalizeProfile);
  const categories = asArray(payload.categories).map(normalizeCategory);
  const documents = asArray(payload.documents).map(normalizeDocument);
  const accounts = asArray(payload.accounts).map(normalizeAccount);
  const runSummary = payload.run_summary && typeof payload.run_summary === "object"
    ? payload.run_summary
    : {};

  return {
    schema,
    schema_version: schemaVersion,
    app: {
      name: asString(payload.app?.name, "UniversalDocsGrabber"),
      version: asString(payload.app?.version, "unbekannt"),
      exported_at: asString(payload.app?.exported_at)
    },
    capabilities: {
      redacted: asBoolean(payload.capabilities?.redacted, true),
      contains_credentials: asBoolean(payload.capabilities?.contains_credentials, false),
      contains_document_files: asBoolean(payload.capabilities?.contains_document_files, false),
      contains_mail_body_text: asBoolean(payload.capabilities?.contains_mail_body_text, false)
    },
    base_path_hint: normalizePathHint(payload.base_path_hint),
    accounts,
    profiles,
    categories,
    documents,
    run_summary: {
      exported_profile_count: asNumber(runSummary.exported_profile_count, profiles.length),
      active_profile_count: asNumber(
        runSummary.active_profile_count,
        profiles.filter((profile) => profile.active).length
      ),
      exported_document_count: asNumber(runSummary.exported_document_count, documents.length),
      scheduler_interval_minutes: asNumber(runSummary.scheduler_interval_minutes, 0),
      profile_stats: asArray(runSummary.profile_stats).map(normalizeProfileStat)
    },
    summary: {
      account_count: accounts.length,
      profile_count: profiles.length,
      category_count: categories.length,
      document_count: documents.length,
      available_count: documents.filter((document) => document.status === "available").length,
      missing_count: documents.filter((document) => document.status === "missing").length
    }
  };
}

export function parseLibraryText(text) {
  if (!asString(text).trim()) {
    throw new Error("Die ausgewählte Datei ist leer.");
  }

  let raw;
  try {
    raw = JSON.parse(text);
  } catch (error) {
    throw new Error("Die Datei ist kein gültiges JSON.");
  }

  return normalizeLibraryPayload(raw);
}

export function formatPathHint(pathHint) {
  const kind = asString(pathHint?.kind, "unknown");
  const value = asString(pathHint?.value);
  if (!value) {
    return "Kein Pfadhinweis";
  }

  if (kind === "relative") {
    return value;
  }

  if (kind === "basename") {
    return `Dateiname: ${value}`;
  }

  return value;
}

export function filterDocuments(documents, filters) {
  const query = asString(filters?.query).trim().toLowerCase();
  const profile = asString(filters?.profile);
  const category = asString(filters?.category);
  const status = asString(filters?.status);

  return documents.filter((document) => {
    if (profile && document.profile_name !== profile) {
      return false;
    }
    if (category && document.category !== category) {
      return false;
    }
    if (status && document.status !== status) {
      return false;
    }

    if (!query) {
      return true;
    }

    const haystack = [
      document.filename,
      document.profile_name,
      document.category,
      document.file_type,
      document.document_date,
      document.path_hint.value
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(query);
  });
}

export function getDemoLibrary() {
  return normalizeLibraryPayload({
    schema: "docsgrabber-library",
    schema_version: "1.0",
    app: {
      name: "UniversalDocsGrabber",
      version: "1.2.0",
      exported_at: "2026-05-28T16:00:00+02:00"
    },
    capabilities: {
      redacted: true,
      contains_credentials: false,
      contains_document_files: false,
      contains_mail_body_text: false
    },
    base_path_hint: {
      kind: "basename",
      value: "UnivDocs"
    },
    accounts: [
      {
        ref: "account-6d9b44",
        profile_count: 2
      }
    ],
    profiles: [
      {
        id: "profile-1",
        name: "Rechnungen",
        group: "Finanzen",
        active: true,
        account_ref: "account-6d9b44",
        target_folder: "Invoices/Rechnungen",
        filters: {
          subject: "Rechnung",
          sender: "billing@example.org",
          since: "2026-05-01",
          gmail_query: "has:attachment label:finance"
        },
        effective_settings: {
          download_attachments: true,
          convert_body_to_pdf: false,
          convert_all_to_pdf: false,
          enable_hash_check: true,
          auto_categorize: true,
          category_rule_count: 2,
          formats: ["pdf", "docx", "png"]
        },
        document_count: 2,
        last_document_date: "2026-05-27"
      },
      {
        id: "profile-2",
        name: "Verträge",
        group: "Organisation",
        active: false,
        account_ref: "account-6d9b44",
        target_folder: "Contracts",
        filters: {
          subject: "Vertrag",
          sender: "",
          since: "2026-04-01",
          gmail_query: ""
        },
        effective_settings: {
          download_attachments: true,
          convert_body_to_pdf: true,
          convert_all_to_pdf: false,
          enable_hash_check: false,
          auto_categorize: true,
          category_rule_count: 1,
          formats: ["pdf", "docx"]
        },
        document_count: 1,
        last_document_date: "2026-05-19"
      }
    ],
    categories: [
      {
        name: "Rechnungen",
        source: "global_rules",
        rule_count: 2,
        document_count: 2
      },
      {
        name: "Verträge",
        source: "path_scan",
        rule_count: 1,
        document_count: 1
      }
    ],
    documents: [
      {
        profile_name: "Rechnungen",
        filename: "rechnung-2026-05.pdf",
        document_date: "2026-05-27",
        file_type: "pdf",
        category: "Rechnungen",
        path_hint: {
          kind: "relative",
          value: "Invoices/Rechnungen/rechnung-2026-05.pdf"
        },
        status: "available",
        sha256: "7b7a26f8d9"
      },
      {
        profile_name: "Rechnungen",
        filename: "mahnung.png",
        document_date: "2026-05-25",
        file_type: "png",
        category: "Rechnungen",
        path_hint: {
          kind: "basename",
          value: "mahnung.png"
        },
        status: "missing",
        sha256: ""
      },
      {
        profile_name: "Verträge",
        filename: "servicevertrag.docx",
        document_date: "2026-05-19",
        file_type: "docx",
        category: "Verträge",
        path_hint: {
          kind: "relative",
          value: "Contracts/servicevertrag.docx"
        },
        status: "available",
        sha256: "55c9fdfe31"
      }
    ],
    run_summary: {
      exported_profile_count: 2,
      active_profile_count: 1,
      exported_document_count: 3,
      scheduler_interval_minutes: 60,
      profile_stats: [
        {
          profile_name: "Rechnungen",
          document_count: 2,
          last_document_date: "2026-05-27",
          active: true
        },
        {
          profile_name: "Verträge",
          document_count: 1,
          last_document_date: "2026-05-19",
          active: false
        }
      ]
    }
  });
}
