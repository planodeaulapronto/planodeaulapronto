"""
Aplica CSS responsivo comum nas paginas principais do site.

Escopo:
- index.html
- artigos/*.html
- produto/*.html
- produtos/*.html
- cidades/index.html
- /{cidade}/index.html e /{cidade}/concurso-*.html
- discipline-pages/*.html

Nao altera links, Hotmart, AulaGen, sitemap ou conteudo de venda.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent

RESPONSIVE_CSS = """<style id="responsive-hotfix">
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body { overflow-x: hidden; }
img, video, canvas { max-width: 100%; height: auto; }
svg { max-width: 100%; height: auto; }
svg[viewBox="0 0 448 512"]:not([width]) { width: 20px; height: 20px; }
* { overflow-wrap: anywhere; }
.hero-content, .content-area, .product-info, .product-detail { min-width: 0; }
.hero h1, h1, h2, h3 { max-width: 100%; overflow-wrap: anywhere; word-break: normal; }
#aulagen-sticky-banner { box-sizing: border-box; }

@media (max-width: 900px) {
  .container, .product-detail, .product-layout, .lead-card, .category-section, .subniche-hub {
    max-width: 100% !important;
  }
  .container, .product-layout {
    grid-template-columns: 1fr !important;
  }
  .content-area, .lead-card, .product-info, .product-detail {
    padding: 22px !important;
  }
  aside, .sidebar {
    width: 100% !important;
    max-width: 100% !important;
  }
  header nav, .nav-bar {
    flex-wrap: wrap !important;
    gap: 10px !important;
  }
}

@media (max-width: 640px) {
  #aulagen-sticky-banner {
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    padding: 10px 12px !important;
  }
  #aulagen-sticky-banner > div {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 10px !important;
  }
  #aulagen-sticky-banner a {
    width: 100% !important;
    box-sizing: border-box !important;
    text-align: center !important;
  }
  .cat-nav {
    top: 116px !important;
    padding: 7px 10px !important;
  }
  .cat-nav-inner, .subtopic-nav-inner {
    justify-content: flex-start !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
  }
  .cat-nav-inner::-webkit-scrollbar,
  .subtopic-nav-inner::-webkit-scrollbar,
  .subniche-products::-webkit-scrollbar {
    display: none !important;
  }
  .cat-btn, .subtopic-btn {
    white-space: nowrap !important;
    flex-shrink: 0 !important;
  }
  .hero {
    padding: 32px 14px 28px !important;
  }
  .hero-content {
    max-width: 100% !important;
    width: 100% !important;
  }
  .hero-stats {
    gap: 16px !important;
  }
  .search-container {
    padding: 0 6px !important;
  }
  h1 {
    font-size: clamp(1.25rem, 6.2vw, 1.65rem) !important;
    line-height: 1.18 !important;
  }
  .hero h1 {
    font-size: clamp(1.15rem, 6vw, 1.45rem) !important;
    max-width: calc(100vw - 28px) !important;
    margin-left: auto !important;
    margin-right: auto !important;
  }
  h2 {
    font-size: clamp(1.15rem, 6vw, 1.55rem) !important;
    line-height: 1.25 !important;
  }
  p, li {
    font-size: 0.98rem !important;
  }
  .products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 8px !important;
    padding: 8px !important;
  }
  .product-card {
    border-radius: 10px !important;
  }
  .card-body {
    padding: 8px !important;
  }
  .card-title {
    font-size: .72rem !important;
  }
  .card-footer {
    align-items: stretch !important;
    flex-direction: column !important;
  }
  .buy-btn, .buy-btn-large {
    width: 100% !important;
    box-sizing: border-box !important;
    display: block !important;
    text-align: center !important;
  }
  .subniche-products {
    grid-auto-columns: minmax(136px, 160px) !important;
  }
  .product-layout {
    display: block !important;
  }
  .product-image-container, .product-info {
    width: 100% !important;
    max-width: 100% !important;
  }
  .side-menu {
    width: min(86vw, 300px) !important;
  }
  .hamburger {
    top: 10px !important;
    right: 10px !important;
  }
  .whatsapp-float {
    max-width: calc(100vw - 24px) !important;
    right: 12px !important;
    left: auto !important;
  }
  [style*="columns"] {
    columns: 1 !important;
  }
  table {
    display: block !important;
    max-width: 100% !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
  }
}
</style>"""


def target_files() -> list[Path]:
    files: list[Path] = []
    for name in ("index.html", "mapa-do-site.html"):
        p = ROOT / name
        if p.exists():
            files.append(p)

    for folder in ("artigos", "produto", "produtos", "discipline-pages"):
        d = ROOT / folder
        if d.exists():
            files.extend(sorted(d.glob("*.html")))

    cidades_index = ROOT / "cidades" / "index.html"
    if cidades_index.exists():
        files.append(cidades_index)

    for d in ROOT.iterdir():
        if d.is_dir() and (d / "concurso-professor.html").exists():
            files.extend(sorted(d.glob("*.html")))

    return files


def patch_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8-sig", errors="ignore")
    before = raw

    start = raw.find('<style id="responsive-hotfix">')
    if start != -1:
        end = raw.find("</style>", start)
        if end != -1:
            raw = raw[:start] + raw[end + len("</style>") :]

    if "</head>" in raw:
        raw = raw.replace("</head>", RESPONSIVE_CSS + "\n</head>", 1)
    else:
        raw = RESPONSIVE_CSS + "\n" + raw

    if raw != before:
        path.write_text(raw, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    files = target_files()
    changed = 0
    for path in files:
        if patch_file(path):
            changed += 1
    print(f"responsive_hotfix_targets={len(files)}")
    print(f"responsive_hotfix_changed={changed}")


if __name__ == "__main__":
    main()
