import {
  filterDocuments,
  formatPathHint,
  getDemoLibrary,
  parseLibraryText
} from "./library.js";

function escHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const I18N = {
  de: {
    app_title_page: "UniversalDocsGrabber Web/PWA-Companion",
    app_eyebrow: "UniversalDocsGrabber Companion",
    app_title: "Mobile Dokumentkontrolle für redigierte Bibliotheksexporte",
    hero_copy: "Der Companion lädt docsgrabber-library-v1.json direkt im Browser, zeigt Profile, Kategorien und Dokumentmetadaten lokal an und bleibt bewusst ohne IMAP-Zugang, PDF-Upload oder Mail-Credentials.",
    badge_no_upload: "Kein Upload",
    badge_offline: "Offline-fähig",
    badge_platforms: "Android / iOS / Web",
    btn_select_export: "Export wählen",
    btn_load_demo: "Demo laden",
    status_initial: "Noch kein Companion-Export geladen.",
    status_loaded: "{source} geladen: {docs} Dokumente aus {profiles} Profilen.",
    status_empty_profiles: "Der Export enthält keine Profile.",
    status_empty_categories: "Der Export enthält keine Kategorien.",
    status_empty_docs: "Keine Dokumente entsprechen den aktuellen Filtern.",
    status_no_docs_loaded: "Noch keine Dokumente geladen.",
    status_no_export_loaded: "Noch kein Export geladen.",
    sec_export: "Export",
    sec_inventory: "Bestand",
    sec_search_eyebrow: "Lokale Suche",
    sec_filter_title: "Dokumente filtern",
    lbl_app: "App",
    lbl_exported_at: "Exportiert",
    lbl_base_path: "Basisordner",
    lbl_interval: "Intervall",
    lbl_profiles: "Profile",
    lbl_active: "Aktiv",
    lbl_documents: "Dokumente",
    lbl_categories: "Kategorien",
    lbl_search: "Suche",
    lbl_profile: "Profil",
    lbl_category: "Kategorie",
    lbl_status: "Status",
    opt_all_profiles: "Alle Profile",
    opt_all_categories: "Alle Kategorien",
    opt_all: "Alle",
    opt_available: "Verfügbar",
    opt_missing: "Fehlt lokal",
    sec_profiles: "Profile",
    sec_categories: "Kategorien",
    sec_doc_index: "Dokumentindex",
    sec_details: "Details",
    badge_readonly: "Read-only",
    detail_empty: "Wähle ein Dokument aus der Liste, um Pfadhinweis, Status und Profilzuordnung zu prüfen.",
    search_placeholder: "Dateiname, Profil oder Pfadhinweis",
    unit_entries: "Einträge",
    unit_hits: "Treffer",
    unit_minutes: "Minuten",
    state_disabled: "Deaktiviert",
    state_unknown: "unbekannt",
    state_no_hint: "ohne Hinweis",
    state_active: "Aktiv",
    state_inactive: "Inaktiv",
    state_no_formats: "keine Formatliste",
    state_auto_cat_on: "Auto-Kategorisierung an",
    state_auto_cat_off: "Auto-Kategorisierung aus",
    state_hash_on: "Hash-Check an",
    state_hash_off: "Hash-Check aus",
    lbl_group_prefix: "Gruppe: ",
    lbl_target_folder_prefix: "Zielordner: ",
    lbl_docs_prefix: "Dokumente: ",
    lbl_last_doc_prefix: "Letztes Dokument: ",
    lbl_color: "Farbe",
    lbl_date_type: "Dateityp",
    lbl_doc_date: "Dokumentdatum",
    lbl_path_hint: "Pfadhinweis",
    lbl_sha256: "SHA-256",
    state_not_exported: "nicht exportiert",
    state_status_ok: "Verfügbar auf diesem Gerät",
    state_status_missing: "Nicht gefunden am angegebenen Pfad",
    lang_label: "Sprache"
  },
  en: {
    app_title_page: "UniversalDocsGrabber Web/PWA Companion",
    app_eyebrow: "UniversalDocsGrabber Companion",
    app_title: "Mobile Document Inspection for Redacted Library Exports",
    hero_copy: "The Companion loads docsgrabber-library-v1.json directly inside your browser, displays profiles, categories, and document metadata locally without IMAP access, PDF uploads, or mail credentials.",
    badge_no_upload: "Zero Upload",
    badge_offline: "Offline-Ready",
    badge_platforms: "Android / iOS / Web",
    btn_select_export: "Choose Export",
    btn_load_demo: "Load Demo",
    status_initial: "No companion export loaded yet.",
    status_loaded: "{source} loaded: {docs} documents from {profiles} profiles.",
    status_empty_profiles: "The export contains no profiles.",
    status_empty_categories: "The export contains no categories.",
    status_empty_docs: "No documents match the active filters.",
    status_no_docs_loaded: "No documents loaded yet.",
    status_no_export_loaded: "No export loaded yet.",
    sec_export: "Export",
    sec_inventory: "Inventory",
    sec_search_eyebrow: "Local Search",
    sec_filter_title: "Filter Documents",
    lbl_app: "App",
    lbl_exported_at: "Exported",
    lbl_base_path: "Base Folder",
    lbl_interval: "Interval",
    lbl_profiles: "Profiles",
    lbl_active: "Active",
    lbl_documents: "Documents",
    lbl_categories: "Categories",
    lbl_search: "Search",
    lbl_profile: "Profile",
    lbl_category: "Category",
    lbl_status: "Status",
    opt_all_profiles: "All Profiles",
    opt_all_categories: "All Categories",
    opt_all: "All",
    opt_available: "Available",
    opt_missing: "Missing Locally",
    sec_profiles: "Profiles",
    sec_categories: "Categories",
    sec_doc_index: "Document Index",
    sec_details: "Details",
    badge_readonly: "Read-only",
    detail_empty: "Select a document from the list to review path hint, status, and profile association.",
    search_placeholder: "Filename, profile, or path hint",
    unit_entries: "entries",
    unit_hits: "hits",
    unit_minutes: "minutes",
    state_disabled: "Disabled",
    state_unknown: "unknown",
    state_no_hint: "no hint",
    state_active: "Active",
    state_inactive: "Inactive",
    state_no_formats: "no format list",
    state_auto_cat_on: "Auto-categorization on",
    state_auto_cat_off: "Auto-categorization off",
    state_hash_on: "Hash-check on",
    state_hash_off: "Hash-check off",
    lbl_group_prefix: "Group: ",
    lbl_target_folder_prefix: "Target folder: ",
    lbl_docs_prefix: "Documents: ",
    lbl_last_doc_prefix: "Latest document: ",
    lbl_color: "Color",
    lbl_date_type: "File type",
    lbl_doc_date: "Document date",
    lbl_path_hint: "Path hint",
    lbl_sha256: "SHA-256",
    state_not_exported: "not exported",
    state_status_ok: "Available on this device",
    state_status_missing: "Not found at specified path",
    lang_label: "Language"
  },
  es: {
    app_title_page: "UniversalDocsGrabber Companion Web/PWA",
    app_eyebrow: "UniversalDocsGrabber Companion",
    app_title: "Control móvil de documentos para exportaciones redactadas",
    hero_copy: "El Companion carga docsgrabber-library-v1.json directamente en el navegador, mostrando perfiles, categorías y metadatos de documentos localmente sin acceso IMAP, subidas de PDF o credenciales.",
    badge_no_upload: "Sin subida",
    badge_offline: "Modo offline",
    badge_platforms: "Android / iOS / Web",
    btn_select_export: "Seleccionar exportación",
    btn_load_demo: "Cargar demo",
    status_initial: "Aún no se ha cargado ninguna exportación.",
    status_loaded: "{source} cargado: {docs} documentos de {profiles} perfiles.",
    status_empty_profiles: "La exportación no contiene perfiles.",
    status_empty_categories: "La exportación no contiene categorías.",
    status_empty_docs: "Ningún documento coincide con los filtros actuales.",
    status_no_docs_loaded: "Aún no se han cargado documentos.",
    status_no_export_loaded: "Aún no se ha cargado una exportación.",
    sec_export: "Exportación",
    sec_inventory: "Inventario",
    sec_search_eyebrow: "Búsqueda local",
    sec_filter_title: "Filtrar documentos",
    lbl_app: "Aplicación",
    lbl_exported_at: "Exportado",
    lbl_base_path: "Carpeta base",
    lbl_interval: "Intervalo",
    lbl_profiles: "Perfiles",
    lbl_active: "Activo",
    lbl_documents: "Documentos",
    lbl_categories: "Categorías",
    lbl_search: "Buscar",
    lbl_profile: "Perfil",
    lbl_category: "Categoría",
    lbl_status: "Estado",
    opt_all_profiles: "Todos los perfiles",
    opt_all_categories: "Todas las categorías",
    opt_all: "Todos",
    opt_available: "Disponible",
    opt_missing: "Falta localmente",
    sec_profiles: "Perfiles",
    sec_categories: "Categorías",
    sec_doc_index: "Índice de documentos",
    sec_details: "Detalles",
    badge_readonly: "Solo lectura",
    detail_empty: "Selecciona un documento de la lista para revisar la pista de ruta, el estado y el perfil.",
    search_placeholder: "Nombre de archivo, perfil o pista de ruta",
    unit_entries: "entradas",
    unit_hits: "coincidencias",
    unit_minutes: "minutos",
    state_disabled: "Desactivado",
    state_unknown: "desconocido",
    state_no_hint: "sin pista",
    state_active: "Activo",
    state_inactive: "Inactivo",
    state_no_formats: "sin formatos",
    state_auto_cat_on: "Auto-categorización activa",
    state_auto_cat_off: "Auto-categorización inactiva",
    state_hash_on: "Verificación hash activa",
    state_hash_off: "Verificación hash inactiva",
    lbl_group_prefix: "Grupo: ",
    lbl_target_folder_prefix: "Carpeta destino: ",
    lbl_docs_prefix: "Documentos: ",
    lbl_last_doc_prefix: "Último documento: ",
    lbl_color: "Color",
    lbl_date_type: "Tipo de archivo",
    lbl_doc_date: "Fecha de documento",
    lbl_path_hint: "Pista de ruta",
    lbl_sha256: "SHA-256",
    state_not_exported: "no exportado",
    state_status_ok: "Disponible en este dispositivo",
    state_status_missing: "No encontrado en la ruta especificada",
    lang_label: "Idioma"
  },
  zh: {
    app_title_page: "UniversalDocsGrabber 网页/PWA伴侣",
    app_eyebrow: "UniversalDocsGrabber Companion",
    app_title: "脱敏库导出清单的移动端文档查验",
    hero_copy: "伴侣直接在浏览器中解析 docsgrabber-library-v1.json，在本地查验配置文件、分类及文档元数据，无需任何 IMAP 访问、PDF 上传或邮箱凭据。",
    badge_no_upload: "零上传",
    badge_offline: "离线可用",
    badge_platforms: "Android / iOS / Web",
    btn_select_export: "选择导出文件",
    btn_load_demo: "加载示例",
    status_initial: "尚未加载伴侣导出文件。",
    status_loaded: "{source} 已加载：包含来自 {profiles} 个配置文件的 {docs} 篇文档。",
    status_empty_profiles: "导出文件中不包含配置文件。",
    status_empty_categories: "导出文件中不包含分类。",
    status_empty_docs: "没有符合当前筛选条件的文档。",
    status_no_docs_loaded: "尚未加载任何文档。",
    status_no_export_loaded: "尚未加载导出文件。",
    sec_export: "导出信息",
    sec_inventory: "资产统计",
    sec_search_eyebrow: "本地检索",
    sec_filter_title: "筛选文档",
    lbl_app: "应用",
    lbl_exported_at: "导出时间",
    lbl_base_path: "基础目录",
    lbl_interval: "抓取间隔",
    lbl_profiles: "配置文件",
    lbl_active: "已启用",
    lbl_documents: "文档总数",
    lbl_categories: "分类总数",
    lbl_search: "搜索",
    lbl_profile: "配置文件",
    lbl_category: "分类",
    lbl_status: "状态",
    opt_all_profiles: "所有配置文件",
    opt_all_categories: "所有分类",
    opt_all: "全部",
    opt_available: "本地可用",
    opt_missing: "本地缺失",
    sec_profiles: "配置文件",
    sec_categories: "分类",
    sec_doc_index: "文档索引",
    sec_details: "详情信息",
    badge_readonly: "只读模式",
    detail_empty: "从列表中选择一篇文档以查看路径提示、状态及归属配置。",
    search_placeholder: "文件名、配置文件或路径提示",
    unit_entries: "项",
    unit_hits: "条匹配",
    unit_minutes: "分钟",
    state_disabled: "已停用",
    state_unknown: "未知",
    state_no_hint: "无路径提示",
    state_active: "已激活",
    state_inactive: "未激活",
    state_no_formats: "无格式列表",
    state_auto_cat_on: "自动分类开启",
    state_auto_cat_off: "自动分类关闭",
    state_hash_on: "哈希校验开启",
    state_hash_off: "哈希校验关闭",
    lbl_group_prefix: "组别：",
    lbl_target_folder_prefix: "目标文件夹：",
    lbl_docs_prefix: "文档数：",
    lbl_last_doc_prefix: "最新文档：",
    lbl_color: "标记颜色",
    lbl_date_type: "文件类型",
    lbl_doc_date: "文档日期",
    lbl_path_hint: "路径提示",
    lbl_sha256: "SHA-256",
    state_not_exported: "未导出",
    state_status_ok: "当前设备上可用",
    state_status_missing: "指定路径下未找到",
    lang_label: "语言"
  },
  ja: {
    app_title_page: "UniversalDocsGrabber Web/PWAコンパニオン",
    app_eyebrow: "UniversalDocsGrabber Companion",
    app_title: "編集済みエクスポートのモバイル文書点検",
    hero_copy: "コンパニオンはブラウザ内で docsgrabber-library-v1.json を直接読み込み、IMAPアクセスやPDFアップロード、メール認証情報なしでプロファイルや文書情報を安全に表示します。",
    badge_no_upload: "アップロードなし",
    badge_offline: "オフライン対応",
    badge_platforms: "Android / iOS / Web",
    btn_select_export: "エクスポートを選択",
    btn_load_demo: "デモを読み込む",
    status_initial: "エクスポートデータはまだ読み込まれていません。",
    status_loaded: "{source} 読込完了：{profiles} プロファイルから {docs} 件の文書。",
    status_empty_profiles: "エクスポートにプロファイルが含まれていません。",
    status_empty_categories: "エクスポートにカテゴリーが含まれていません。",
    status_empty_docs: "現在のフィルターに一致する文書はありません。",
    status_no_docs_loaded: "文書はまだ読み込まれていません。",
    status_no_export_loaded: "エクスポートはまだ読み込まれていません。",
    sec_export: "エクスポート",
    sec_inventory: "登録情報",
    sec_search_eyebrow: "ローカル検索",
    sec_filter_title: "文書フィルター",
    lbl_app: "アプリ",
    lbl_exported_at: "出力日時",
    lbl_base_path: "保存基準フォルダ",
    lbl_interval: "取得間隔",
    lbl_profiles: "プロファイル",
    lbl_active: "有効",
    lbl_documents: "文書数",
    lbl_categories: "カテゴリー",
    lbl_search: "検索",
    lbl_profile: "プロファイル",
    lbl_category: "カテゴリー",
    lbl_status: "ステータス",
    opt_all_profiles: "すべてのプロファイル",
    opt_all_categories: "すべてのカテゴリー",
    opt_all: "すべて",
    opt_available: "利用可能",
    opt_missing: "未検出",
    sec_profiles: "プロファイル",
    sec_categories: "カテゴリー",
    sec_doc_index: "文書インデックス",
    sec_details: "詳細情報",
    badge_readonly: "読取専用",
    detail_empty: "一覧から文書を選択して、パスのヒントやステータスを確認してください。",
    search_placeholder: "ファイル名、プロファイル、またはパスヒント",
    unit_entries: "件",
    unit_hits: "件一致",
    unit_minutes: "分",
    state_disabled: "無効",
    state_unknown: "不明",
    state_no_hint: "ヒントなし",
    state_active: "有効",
    state_inactive: "無効",
    state_no_formats: "フォーマット設定なし",
    state_auto_cat_on: "自動分類オン",
    state_auto_cat_off: "自動分類オフ",
    state_hash_on: "ハッシュ検証オン",
    state_hash_off: "ハッシュ検証オフ",
    lbl_group_prefix: "グループ: ",
    lbl_target_folder_prefix: "保存先: ",
    lbl_docs_prefix: "文書数: ",
    lbl_last_doc_prefix: "最新文書: ",
    lbl_color: "カラー",
    lbl_date_type: "ファイル種類",
    lbl_doc_date: "文書日付",
    lbl_path_hint: "パスヒント",
    lbl_sha256: "SHA-256",
    state_not_exported: "未出力",
    state_status_ok: "この端末で利用可能",
    state_status_missing: "指定パスに見つかりません",
    lang_label: "言語"
  },
  ru: {
    app_title_page: "UniversalDocsGrabber Веб/PWA компаньон",
    app_eyebrow: "UniversalDocsGrabber Companion",
    app_title: "Мобильный контроль очищенных библиотек документов",
    hero_copy: "Компаньон открывает docsgrabber-library-v1.json прямо в браузере, локально отображая профили, категории и метаданные документов без IMAP, загрузки файлов или передачи паролей.",
    badge_no_upload: "Без выгрузки",
    badge_offline: "Офлайн-режим",
    badge_platforms: "Android / iOS / Web",
    btn_select_export: "Выбрать экспорт",
    btn_load_demo: "Загрузить демо",
    status_initial: "Экспорт компаньона еще не загружен.",
    status_loaded: "{source} загружен: {docs} документов из {profiles} профилей.",
    status_empty_profiles: "Экспорт не содержит профилей.",
    status_empty_categories: "Экспорт не содержит категорий.",
    status_empty_docs: "Нет документов, соответствующих заданным фильтрам.",
    status_no_docs_loaded: "Документы еще не загружены.",
    status_no_export_loaded: "Экспорт еще не загружен.",
    sec_export: "Экспорт",
    sec_inventory: "Учет",
    sec_search_eyebrow: "Локальный поиск",
    sec_filter_title: "Фильтрация документов",
    lbl_app: "Приложение",
    lbl_exported_at: "Экспортировано",
    lbl_base_path: "Базовый каталог",
    lbl_interval: "Интервал",
    lbl_profiles: "Профили",
    lbl_active: "Активно",
    lbl_documents: "Документы",
    lbl_categories: "Категории",
    lbl_search: "Поиск",
    lbl_profile: "Профиль",
    lbl_category: "Категория",
    lbl_status: "Статус",
    opt_all_profiles: "Все профили",
    opt_all_categories: "Все категории",
    opt_all: "Все",
    opt_available: "Доступно",
    opt_missing: "Отсутствует",
    sec_profiles: "Профили",
    sec_categories: "Категории",
    sec_doc_index: "Список документов",
    sec_details: "Сведения",
    badge_readonly: "Только чтение",
    detail_empty: "Выберите документ из списка для просмотра пути, статуса и профиля.",
    search_placeholder: "Имя файла, профиль или путь",
    unit_entries: "записей",
    unit_hits: "совпадений",
    unit_minutes: "минут",
    state_disabled: "Отключено",
    state_unknown: "неизвестно",
    state_no_hint: "без пути",
    state_active: "Активно",
    state_inactive: "Неактивно",
    state_no_formats: "нет форматов",
    state_auto_cat_on: "Автокатегоризация вкл.",
    state_auto_cat_off: "Автокатегоризация выкл.",
    state_hash_on: "Проверка хэша вкл.",
    state_hash_off: "Проверка хэша выкл.",
    lbl_group_prefix: "Группа: ",
    lbl_target_folder_prefix: "Каталог: ",
    lbl_docs_prefix: "Документы: ",
    lbl_last_doc_prefix: "Последний документ: ",
    lbl_color: "Цвет",
    lbl_date_type: "Тип файла",
    lbl_doc_date: "Дата документа",
    lbl_path_hint: "Путь",
    lbl_sha256: "SHA-256",
    state_not_exported: "не экспортировано",
    state_status_ok: "Доступно на этом устройстве",
    state_status_missing: "Не найдено по указанному пути",
    lang_label: "Язык"
  }
};

let currentLang = "de";

function t(key, params = {}) {
  const dict = I18N[currentLang] || I18N.de;
  let text = dict[key] || I18N.en[key] || I18N.de[key] || key;
  for (const [k, v] of Object.entries(params)) {
    text = text.replace(new RegExp(`\\{${k}\\}`, "g"), v);
  }
  return text;
}

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
  statusFilter: document.querySelector("#status-filter"),
  langSelect: document.querySelector("#lang-select")
};

let currentPayload = null;
let currentSourceLabel = "";
let selectedDocumentId = "";

function applyLanguage(lang) {
  if (!I18N[lang]) {
    lang = "de";
  }
  currentLang = lang;
  try {
    localStorage.setItem("udg_lang", lang);
  } catch (e) {
    // Local storage unavailable
  }

  if (elements.langSelect && elements.langSelect.value !== lang) {
    elements.langSelect.value = lang;
  }
  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const k = node.getAttribute("data-i18n");
    if (k && I18N[lang][k]) {
      node.textContent = I18N[lang][k];
    }
  });

  document.querySelectorAll("[data-i18n-ph]").forEach((node) => {
    const k = node.getAttribute("data-i18n-ph");
    if (k && I18N[lang][k]) {
      node.placeholder = I18N[lang][k];
    }
  });

  if (currentPayload) {
    renderSummaries(currentPayload);
    renderProfiles(currentPayload);
    renderCategories(currentPayload);
    updateFilterOptions(currentPayload);
    applyFilters();
    setStatus(t("status_loaded", {
      source: currentSourceLabel,
      docs: currentPayload.summary.document_count,
      profiles: currentPayload.summary.profile_count
    }));
  }
}

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
  const exportedAt = payload.app.exported_at || t("state_unknown");
  const basePath = payload.base_path_hint.value || t("state_no_hint");
  const interval = payload.run_summary.scheduler_interval_minutes
    ? `${payload.run_summary.scheduler_interval_minutes} ${t("unit_minutes")}`
    : t("state_disabled");

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
  elements.profileBadge.textContent = `${payload.profiles.length} ${t("unit_entries")}`;

  if (!payload.profiles.length) {
    elements.profileList.className = "stacked-list empty-state";
    elements.profileList.textContent = t("status_empty_profiles");
    return;
  }

  elements.profileList.className = "stacked-list";
  elements.profileList.innerHTML = "";

  payload.profiles.forEach((profile) => {
    const article = document.createElement("article");
    article.className = "profile-card";

    const formatBadge = profile.effective_settings.formats.length
      ? profile.effective_settings.formats.join(", ")
      : t("state_no_formats");

    article.innerHTML = `
      <div class="card-topline">
        <div class="card-title">${escHtml(profile.name)}</div>
        <span class="pill">${profile.active ? t("state_active") : t("state_inactive")}</span>
      </div>
      <div class="meta-row">
        <div>${t("lbl_group_prefix")}${escHtml(profile.group)}</div>
        <div>${t("lbl_target_folder_prefix")}${escHtml(profile.target_folder || t("state_no_hint"))}</div>
        <div>${t("lbl_docs_prefix")}${escHtml(profile.document_count)}</div>
        <div>${t("lbl_last_doc_prefix")}${escHtml(profile.last_document_date || t("state_unknown"))}</div>
      </div>
      <div class="meta-pills">
        <span class="meta-pill">${escHtml(formatBadge)}</span>
        <span class="meta-pill">${profile.effective_settings.auto_categorize ? t("state_auto_cat_on") : t("state_auto_cat_off")}</span>
        <span class="meta-pill">${profile.effective_settings.enable_hash_check ? t("state_hash_on") : t("state_hash_off")}</span>
      </div>
    `;

    elements.profileList.append(article);
  });
}

function renderCategories(payload) {
  elements.categoryBadge.textContent = `${payload.categories.length} ${t("unit_entries")}`;

  if (!payload.categories.length) {
    elements.categoryList.className = "stacked-list empty-state";
    elements.categoryList.textContent = t("status_empty_categories");
    return;
  }

  elements.categoryList.className = "stacked-list";
  elements.categoryList.innerHTML = "";

  payload.categories.forEach((category) => {
    const article = document.createElement("article");
    article.className = "category-card";
    article.innerHTML = `
      <div class="card-topline">
        <div class="card-title">${escHtml(category.name)}</div>
        <span class="pill">${category.document_count} ${t("lbl_documents")}</span>
      </div>
      <div class="meta-row">
        <div>${t("lbl_color")}: ${escHtml(category.color || "default")}</div>
      </div>
    `;

    elements.categoryList.append(article);
  });
}

function renderDocumentDetail(document) {
  if (!document) {
    elements.documentDetail.className = "detail-card empty-state";
    elements.documentDetail.textContent = t("detail_empty");
    return;
  }

  elements.documentDetail.className = "detail-card";

  const isAvailable = document.status !== "missing";
  const pathHintLabel = isAvailable ? t("state_status_ok") : t("state_status_missing");

  elements.documentDetail.innerHTML = `
    <div class="detail-header">
      <div>
        <p class="eyebrow subtle">${escHtml(document.profile_name)}</p>
        <div class="detail-title">${escHtml(document.filename)}</div>
      </div>
      <span class="pill ${document.status === "missing" ? "warning" : ""}">${document.status === "missing" ? t("opt_missing") : t("opt_available")}</span>
    </div>

    <dl class="facts-grid detail-facts">
      <dt>${t("lbl_profile")}</dt>
      <dd>${escHtml(document.profile_name)}</dd>
      <dt>${t("lbl_category")}</dt>
      <dd>${escHtml(document.category)}</dd>
      <dt>${t("lbl_date_type")}</dt>
      <dd>${escHtml(document.file_type || t("state_unknown"))}</dd>
      <dt>${t("lbl_doc_date")}</dt>
      <dd>${escHtml(document.document_date || t("state_unknown"))}</dd>
      <dt>${escHtml(pathHintLabel)}</dt>
      <dd>${escHtml(formatPathHint(document.path_hint))}</dd>
      <dt>${t("lbl_sha256")}</dt>
      <dd>${escHtml(document.sha256 || t("state_not_exported"))}</dd>
    </dl>
  `;
}

function renderDocuments(documents) {
  elements.documentBadge.textContent = `${documents.length} ${t("unit_entries")}`;
  elements.resultBadge.textContent = `${documents.length} ${t("unit_hits")}`;

  if (!documents.length) {
    elements.documentList.className = "stacked-list empty-state";
    elements.documentList.textContent = t("status_empty_docs");
    renderDocumentDetail(null);
    return;
  }

  const selected = documents.find((doc) => doc.id === selectedDocumentId) || documents[0];
  selectedDocumentId = selected.id;

  elements.documentList.className = "stacked-list";
  elements.documentList.innerHTML = "";

  documents.forEach((doc) => {
    const article = document.createElement("article");
    article.className = `document-card${doc.id === selectedDocumentId ? " is-selected" : ""}`;

    const statusClass = doc.status === "missing" ? "warning" : "";
    const statusLabel = doc.status === "missing" ? t("opt_missing") : t("opt_available");

    article.innerHTML = `
      <div class="card-topline">
        <div class="card-title">${escHtml(doc.filename)}</div>
        <span class="meta-pill ${statusClass}">${statusLabel}</span>
      </div>
      <div class="meta-row">
        <div>${t("lbl_profile")}: ${escHtml(doc.profile_name)}</div>
        <div>${t("lbl_category")}: ${escHtml(doc.category)}</div>
        <div>${t("lbl_date_type")}: ${escHtml(doc.file_type || t("state_unknown"))}</div>
        <div>${t("lbl_doc_date")}: ${escHtml(doc.document_date || t("state_unknown"))}</div>
      </div>
      <div class="meta-row">
        <div>${escHtml(formatPathHint(doc.path_hint))}</div>
      </div>
    `;

    article.addEventListener("click", () => {
      selectedDocumentId = doc.id;
      applyFilters();
    });

    elements.documentList.append(article);
  });

  renderDocumentDetail(selected);
}

function updateFilterOptions(payload) {
  const currentProfile = elements.profileFilter.value;
  const currentCategory = elements.categoryFilter.value;

  const profiles = payload.profiles.map((profile) => profile.name);
  const categories = payload.categories.map((category) => category.name);

  elements.profileFilter.innerHTML = `<option value="">${t("opt_all_profiles")}</option>`;
  profiles.forEach((profile) => {
    const option = document.createElement("option");
    option.value = profile;
    option.textContent = profile;
    if (profile === currentProfile) {
      option.selected = true;
    }
    elements.profileFilter.append(option);
  });

  elements.categoryFilter.innerHTML = `<option value="">${t("opt_all_categories")}</option>`;
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    if (category === currentCategory) {
      option.selected = true;
    }
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
  currentSourceLabel = sourceLabel;
  selectedDocumentId = "";
  setStatus(t("status_loaded", {
    source: sourceLabel,
    docs: payload.summary.document_count,
    profiles: payload.summary.profile_count
  }));
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

if (elements.langSelect) {
  elements.langSelect.addEventListener("change", (event) => {
    applyLanguage(event.target.value);
  });
}

[elements.searchInput, elements.profileFilter, elements.categoryFilter, elements.statusFilter].forEach((element) => {
  element.addEventListener("input", applyFilters);
  element.addEventListener("change", applyFilters);
});

const params = new URLSearchParams(window.location.search);
if (params.get("demo") === "1") {
  renderPayload(getDemoLibrary(), "Demo-Export");
}

let savedLang = "de";
try {
  savedLang = localStorage.getItem("udg_lang") || "de";
} catch (e) {
  savedLang = "de";
}
applyLanguage(savedLang);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      // Offline-Support ist optional; der Companion bleibt auch ohne Service Worker nutzbar.
    });
  });
}
