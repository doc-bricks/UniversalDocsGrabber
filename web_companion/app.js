import {
  filterDocuments,
  formatPathHint,
  getDemoLibrary,
  parseLibraryText
} from "./library.js";

const elements = {
  categoryBadge: document.querySelector("#category-badge"),
  categoryFilter: document.querySelector("#category-filter"),
  categoryList: document.querySelector("#category-list"),
  countSummary: document.querySelector("#count-summary"),
  detailBadge: document.querySelector("#detail-badge"),
  documentBadge: document.querySelector("#document-badge"),
  documentDetail: document.querySelector("#document-detail"),
  documentList: document.querySelector("#document-list"),
  exportSummary: document.querySelector("#export-summary"),
  fileInput: document.querySelector("#library-file"),
  loadDemo: document.querySelector("#load-demo"),
  profileBadge: document.querySelector("#profile-badge"),
  profileFilter: document.querySelector("#profile-filter"),
  profileList: document.querySelector("#profile-list"),
  resultBadge: document.querySelector("#result-badge"),
  searchInput: document.querySelector("#search-input"),
  status: document.querySelector("#status-message"),
  statusFilter: document.querySelector("#status-filter")
};

let currentPayload = null;
let selectedDocumentId = "";

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.style.color = isError ? "#b42318" : "";
}

function updateDefinitionList(container, values) {
  [...container.querySelectorAll("dd")].forEach((node, index) => {
    node.textContent = values[index] || "-";
  });
}

function renderSummaries(payload) {
  const exportedAt = payload.app.exported_at || "unbekannt";
  const basePath = payload.base_path_hint.value || "ohne Hinweis";
  const interval = payload.run_summary.scheduler_interval_minutes
    ? `${payload.run_summary.scheduler_interval_minutes} Minuten`
    : "Deaktiviert";

  updateDefinitionList(elements.exportSummary, [
    `${payload.app.name} ${payload.app.version}`,
    exportedAt,
    basePath,
    interval
  ]);

  updateDefinitionList(elements.countSummary, [
    String(payload.summary.profile_count),
    String(payload.run_summary.active_profile_count),
    String(payload.summary.document_count),
    String(payload.summary.category_count)
  ]);
}

function renderProfiles(payload) {
  elements.profileBadge.textContent = `${payload.profiles.length} Einträge`;

  if (!payload.profiles.length) {
    elements.profileList.className = "stacked-list empty-state";
    elements.profileList.textContent = "Der Export enthält keine Profile.";
    return;
  }

  elements.profileList.className = "stacked-list";
  elements.profileList.innerHTML = "";

  payload.profiles.forEach((profile) => {
    const article = document.createElement("article");
    article.className = "profile-card";

    const formatBadge = profile.effective_settings.formats.length
      ? profile.effective_settings.formats.join(", ")
      : "keine Formatliste";

    article.innerHTML = `
      <div class="card-topline">
        <div class="card-title">${profile.name}</div>
        <span class="pill">${profile.active ? "Aktiv" : "Inaktiv"}</span>
      </div>
      <div class="meta-row">
        <div>Gruppe: ${profile.group}</div>
        <div>Zielordner: ${profile.target_folder || "kein Ordnerhinweis"}</div>
        <div>Dokumente: ${profile.document_count}</div>
        <div>Letztes Dokument: ${profile.last_document_date || "unbekannt"}</div>
      </div>
      <div class="meta-pills">
        <span class="meta-pill">${formatBadge}</span>
        <span class="meta-pill">${profile.effective_settings.auto_categorize ? "Auto-Kategorisierung an" : "Auto-Kategorisierung aus"}</span>
        <span class="meta-pill">${profile.effective_settings.enable_hash_check ? "Hash-Check an" : "Hash-Check aus"}</span>
      </div>
    `;

    elements.profileList.append(article);
  });
}

function renderCategories(payload) {
  elements.categoryBadge.textContent = `${payload.categories.length} Einträge`;

  if (!payload.categories.length) {
    elements.categoryList.className = "stacked-list empty-state";
    elements.categoryList.textContent = "Der Export enthält keine Kategorien.";
    return;
  }

  elements.categoryList.className = "stacked-list";
  elements.categoryList.innerHTML = "";

  payload.categories.forEach((category) => {
    const article = document.createElement("article");
    article.className = "category-card";
    article.innerHTML = `
      <div class="card-topline">
        <div class="card-title">${category.name}</div>
        <span class="pill soft">${category.document_count} Dokumente</span>
      </div>
      <div class="meta-row">
        <div>Quelle: ${category.source || "unbekannt"}</div>
        <div>Regeln: ${category.rule_count}</div>
      </div>
    `;
    elements.categoryList.append(article);
  });
}

function renderDocumentDetail(document) {
  if (!document) {
    elements.detailBadge.textContent = "Read-only";
    elements.documentDetail.className = "detail-card empty-state";
    elements.documentDetail.textContent =
      "Wähle ein Dokument aus der Liste, um Pfadhinweis, Status und Profilzuordnung zu prüfen.";
    return;
  }

  const pathHintLabel = document.path_hint.kind === "relative" ? "Relativer Pfadhinweis" : "Redigierter Pfadhinweis";
  elements.detailBadge.textContent = document.status === "missing" ? "Fehlt lokal" : "Verfügbar";
  elements.documentDetail.className = "detail-card";
  elements.documentDetail.innerHTML = `
    <div class="card-topline">
      <div class="card-title">${document.filename}</div>
      <span class="meta-pill ${document.status === "missing" ? "danger" : ""}">
        ${document.status === "missing" ? "Fehlt lokal" : "Lokal vorhanden"}
      </span>
    </div>
    <dl class="detail-list">
      <dt>Profil</dt>
      <dd>${document.profile_name}</dd>
      <dt>Kategorie</dt>
      <dd>${document.category}</dd>
      <dt>Dateityp</dt>
      <dd>${document.file_type || "unbekannt"}</dd>
      <dt>Dokumentdatum</dt>
      <dd>${document.document_date || "unbekannt"}</dd>
      <dt>${pathHintLabel}</dt>
      <dd>${formatPathHint(document.path_hint)}</dd>
      <dt>SHA-256</dt>
      <dd>${document.sha256 || "nicht exportiert"}</dd>
    </dl>
  `;
}

function renderDocuments(documents) {
  elements.documentBadge.textContent = `${documents.length} Einträge`;
  elements.resultBadge.textContent = `${documents.length} Treffer`;

  if (!documents.length) {
    elements.documentList.className = "stacked-list empty-state";
    elements.documentList.textContent = "Keine Dokumente entsprechen den aktuellen Filtern.";
    renderDocumentDetail(null);
    return;
  }

  const selected = documents.find((document) => document.id === selectedDocumentId) || documents[0];
  selectedDocumentId = selected.id;

  elements.documentList.className = "stacked-list";
  elements.documentList.innerHTML = "";

  documents.forEach((document) => {
    const article = document.createElement("article");
    article.className = `document-card${document.id === selectedDocumentId ? " is-selected" : ""}`;

    const statusClass = document.status === "missing" ? "warning" : "";
    const statusLabel = document.status === "missing" ? "Fehlt lokal" : "Verfügbar";

    article.innerHTML = `
      <div class="card-topline">
        <div class="card-title">${document.filename}</div>
        <span class="meta-pill ${statusClass}">${statusLabel}</span>
      </div>
      <div class="meta-row">
        <div>Profil: ${document.profile_name}</div>
        <div>Kategorie: ${document.category}</div>
        <div>Dateityp: ${document.file_type || "unbekannt"}</div>
        <div>Datum: ${document.document_date || "unbekannt"}</div>
      </div>
      <div class="meta-row">
        <div>${formatPathHint(document.path_hint)}</div>
      </div>
    `;

    article.addEventListener("click", () => {
      selectedDocumentId = document.id;
      applyFilters();
    });

    elements.documentList.append(article);
  });

  renderDocumentDetail(selected);
}

function updateFilterOptions(payload) {
  const profiles = payload.profiles.map((profile) => profile.name);
  const categories = payload.categories.map((category) => category.name);

  elements.profileFilter.innerHTML = '<option value="">Alle Profile</option>';
  profiles.forEach((profile) => {
    const option = document.createElement("option");
    option.value = profile;
    option.textContent = profile;
    elements.profileFilter.append(option);
  });

  elements.categoryFilter.innerHTML = '<option value="">Alle Kategorien</option>';
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    elements.categoryFilter.append(option);
  });
}

function applyFilters() {
  if (!currentPayload) {
    return;
  }

  const filtered = filterDocuments(currentPayload.documents, {
    query: elements.searchInput.value,
    profile: elements.profileFilter.value,
    category: elements.categoryFilter.value,
    status: elements.statusFilter.value
  });

  renderDocuments(filtered);
}

function renderPayload(payload, sourceLabel) {
  currentPayload = payload;
  selectedDocumentId = "";
  setStatus(`${sourceLabel} geladen: ${payload.summary.document_count} Dokumente aus ${payload.summary.profile_count} Profilen.`);
  renderSummaries(payload);
  renderProfiles(payload);
  renderCategories(payload);
  updateFilterOptions(payload);
  applyFilters();
}

async function handleFile(file) {
  if (!file) {
    return;
  }

  try {
    const text = await file.text();
    const payload = parseLibraryText(text);
    renderPayload(payload, file.name);
  } catch (error) {
    setStatus(error.message, true);
  }
}

elements.fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files || [];
  void handleFile(file);
});

elements.loadDemo.addEventListener("click", () => {
  renderPayload(getDemoLibrary(), "Demo-Export");
});

[elements.searchInput, elements.profileFilter, elements.categoryFilter, elements.statusFilter].forEach((element) => {
  element.addEventListener("input", applyFilters);
  element.addEventListener("change", applyFilters);
});

const params = new URLSearchParams(window.location.search);
if (params.get("demo") === "1") {
  renderPayload(getDemoLibrary(), "Demo-Export");
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      // Offline-Support ist optional; der Companion bleibt auch ohne Service Worker nutzbar.
    });
  });
}
