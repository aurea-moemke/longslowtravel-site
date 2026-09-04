const supportedLanguages = ["en", "de", "es", "fr", "it", "pt"];
const scriptURL = new URL(document.currentScript.src);

function storedLanguage() {
  try {
    return window.localStorage.getItem("lst-site-language");
  } catch {
    return null;
  }
}

function preferredLanguage() {
  const requested = new URLSearchParams(window.location.search).get("lang");
  if (supportedLanguages.includes(requested)) return requested;

  const stored = storedLanguage();
  if (supportedLanguages.includes(stored)) return stored;

  const browserLanguages = navigator.languages || [navigator.language];
  return browserLanguages
    .map((language) => language.toLowerCase().split("-")[0])
    .find((language) => supportedLanguages.includes(language)) || "en";
}

function translateTextNodes(root, strings) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);

  nodes.forEach((node) => {
    if (node.parentElement?.closest("script, style, [data-no-translate]")) return;

    const source = node.nodeValue.trim();
    const translation = strings[source];
    if (source && translation) {
      node.nodeValue = node.nodeValue.replace(source, translation);
    }
  });
}

function translateAttributes(root, strings) {
  root.querySelectorAll("[aria-label], [alt], [title], [placeholder]").forEach((element) => {
    if (element.closest("[data-no-translate]")) return;

    ["aria-label", "alt", "title", "placeholder"].forEach((attribute) => {
      const source = element.getAttribute(attribute);
      if (source && strings[source]) element.setAttribute(attribute, strings[source]);
    });
  });
}

function updateMetadata(metadata) {
  if (!metadata) return;

  document.title = metadata.title;
  const description = document.querySelector('meta[name="description"]');
  const openGraphTitle = document.querySelector('meta[property="og:title"]');
  const openGraphDescription = document.querySelector('meta[property="og:description"]');

  if (description) description.content = metadata.description;
  if (openGraphTitle) openGraphTitle.content = metadata.title;
  if (openGraphDescription) openGraphDescription.content = metadata.description;
}

function localizedURL(url, language) {
  if (url.origin !== window.location.origin || !["http:", "https:"].includes(url.protocol)) return url;

  if (language === "en") {
    url.searchParams.delete("lang");
  } else {
    url.searchParams.set("lang", language);
  }
  return url;
}

function preserveLanguageInLinks(language) {
  document.querySelectorAll('a[href]:not([href^="#"]):not([href^="mailto:"]):not([href^="tel:"])').forEach((link) => {
    link.href = localizedURL(new URL(link.href, window.location.href), language).href;
  });
}

function addLanguageAlternates(language, page) {
  const canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical || !["home", "support"].includes(page)) return;

  supportedLanguages.forEach((code) => {
    const alternate = document.createElement("link");
    alternate.rel = "alternate";
    alternate.hreflang = code;
    alternate.href = localizedURL(new URL(canonical.href), code).href;
    document.head.appendChild(alternate);
  });

  const fallback = document.createElement("link");
  fallback.rel = "alternate";
  fallback.hreflang = "x-default";
  fallback.href = localizedURL(new URL(canonical.href), "en").href;
  document.head.appendChild(fallback);

  canonical.href = localizedURL(new URL(canonical.href), language).href;
}

function addLanguageSelector(language, catalog) {
  const nav = document.querySelector(".primary-nav");
  if (!nav) return;

  const wrapper = document.createElement("label");
  wrapper.className = "language-picker";

  const label = document.createElement("span");
  label.className = "sr-only";
  label.textContent = catalog.ui[language].languageLabel;

  const select = document.createElement("select");
  select.setAttribute("aria-label", catalog.ui[language].languageLabel);
  select.title = catalog.ui[language].languageLabel;

  supportedLanguages.forEach((code) => {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = catalog.languages[code];
    option.selected = code === language;
    select.appendChild(option);
  });

  select.addEventListener("change", () => {
    try {
      window.localStorage.setItem("lst-site-language", select.value);
    } catch {
      // The URL still preserves the choice when storage is unavailable.
    }
    window.location.assign(localizedURL(new URL(window.location.href), select.value).href);
  });

  wrapper.append(label, select);
  nav.appendChild(wrapper);
}

function showLegalLanguageNotice(language, catalog) {
  const page = document.body.dataset.page;
  const sourceLanguage = document.body.dataset.sourceLanguage;
  const notice = document.querySelector("[data-language-notice]");

  if (!notice || !sourceLanguage || language === sourceLanguage) return;

  notice.textContent = catalog.ui[language].legalNotices[page];
  notice.hidden = false;
}

async function localizePage() {
  const language = preferredLanguage();
  const page = document.body.dataset.page;
  document.documentElement.lang = language;

  try {
    const response = await fetch(new URL("translations.json", scriptURL));
    if (!response.ok) throw new Error(`Translation catalog returned ${response.status}`);

    const catalog = await response.json();
    const strings = {
      ...(catalog.shared[language] || {}),
      ...(catalog.pages[page]?.[language] || {}),
    };

    translateTextNodes(document.body, strings);
    translateAttributes(document.body, strings);
    updateMetadata(catalog.metadata[page]?.[language]);
    preserveLanguageInLinks(language);
    addLanguageAlternates(language, page);
    addLanguageSelector(language, catalog);
    showLegalLanguageNotice(language, catalog);
  } catch (error) {
    console.warn("LST website localization could not be loaded.", error);
  }
}

const navToggle = document.querySelector('.nav-toggle');
const primaryNav = document.querySelector('.primary-nav');

if (navToggle && primaryNav) {
  navToggle.addEventListener('click', () => {
    const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', String(!isOpen));
    primaryNav.classList.toggle('is-open', !isOpen);
  });

  primaryNav.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      navToggle.setAttribute('aria-expanded', 'false');
      primaryNav.classList.remove('is-open');
    }
  });
}

document.querySelectorAll('[data-current-year]').forEach((element) => {
  element.textContent = new Date().getFullYear();
});

localizePage();
