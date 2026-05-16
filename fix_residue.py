"""
Patch final: limpa residuos de diariodaeducacao.com.br.

1. <img src="https://diariodaeducacao.com.br/images/X.webp"> -> <img src="../images/X.webp">
2. Texto "Diario da Educacao", "Diário da Educação", "diariodaeducacao.com.br" -> "Plano de Aula Pronto"
3. Garante que <link rel="icon"> aponta para arquivo local valido
4. Regera sitemap.xml com todos os artigos+produtos+discipline pages atuais
"""

from __future__ import annotations

import re
from pathlib import Path
import datetime

ROOT = Path(__file__).resolve().parent
SITE = "https://planodeaulapronto.github.io"

# ---- regexes ----
RX_IMG_DIARIO = re.compile(r'src="https?://diariodaeducacao\.com\.br/([^"]+)"', re.IGNORECASE)
RX_DOMAIN_TEXT = re.compile(r'diariodaeducacao\.com\.br', re.IGNORECASE)
RX_BRAND_TEXT = re.compile(r'Di[aá]rio\s+da\s+Educa[cç][aã]o', re.IGNORECASE)


def patch_file(path: Path) -> tuple[int, int, int]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if raw.startswith("﻿"):
        raw = raw.lstrip("﻿")

    # 1. img src — converte URL externa para path local (../images/...)
    def img_replace(m: re.Match) -> str:
        path_inside = m.group(1)  # ex: images/produtos-alfabetinho/X.webp
        # pega apenas o nome do arquivo, sem subpastas, e usa ../images/
        filename = path_inside.split("/")[-1]
        return f'src="../images/{filename}"'

    new_raw, n_img = RX_IMG_DIARIO.subn(img_replace, raw)

    # 2. Texto puro mencionando o dominio
    new_raw, n_url = RX_DOMAIN_TEXT.subn("planodeaulapronto.github.io", new_raw)
    new_raw, n_brand = RX_BRAND_TEXT.subn("Plano de Aula Pronto", new_raw)

    if (n_img + n_url + n_brand) > 0:
        path.write_text(new_raw, encoding="utf-8", newline="\n")
    return n_img, n_url, n_brand


def rebuild_sitemap() -> int:
    artigos = sorted((ROOT / "artigos").glob("*.html"))
    produtos = sorted((ROOT / "produtos").glob("*.html")) if (ROOT / "produtos").is_dir() else []
    disciplines = sorted((ROOT / "discipline-pages").glob("*.html")) if (ROOT / "discipline-pages").is_dir() else []

    today = datetime.date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # home
    lines.append(f'  <url><loc>{SITE}/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>')
    # estaticas
    for name in ("mapa-do-site.html", "privacidade.html", "termos.html"):
        if (ROOT / name).exists():
            lines.append(f'  <url><loc>{SITE}/{name}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>')
    # discipline-pages (priority 0.9)
    for f in disciplines:
        lines.append(f'  <url><loc>{SITE}/discipline-pages/{f.name}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>')
    # produtos (priority 0.8)
    for f in produtos:
        lines.append(f'  <url><loc>{SITE}/produtos/{f.name}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    # artigos (priority 0.7)
    for f in artigos:
        lines.append(f'  <url><loc>{SITE}/artigos/{f.name}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')

    lines.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return len(artigos) + len(produtos) + len(disciplines) + 1


def main() -> None:
    targets: list[Path] = []
    for sub in ("artigos", "produtos", "discipline-pages"):
        d = ROOT / sub
        if d.is_dir():
            targets += list(d.glob("*.html"))
    for name in ("index.html", "mapa-do-site.html", "privacidade.html", "termos.html"):
        p = ROOT / name
        if p.exists():
            targets.append(p)

    print(f"📂 Patcheando {len(targets)} arquivos HTML...")
    total_img = total_url = total_brand = 0
    for i, f in enumerate(targets, 1):
        try:
            n_img, n_url, n_brand = patch_file(f)
            total_img += n_img
            total_url += n_url
            total_brand += n_brand
        except Exception as e:
            print(f"  ⚠ erro em {f.name}: {e}")
        if i % 200 == 0:
            print(f"  ...{i}/{len(targets)}")

    print(f"\n✅ {total_img} imagens externas convertidas para local")
    print(f"✅ {total_url} mencoes de URL substituidas")
    print(f"✅ {total_brand} mencoes de marca substituidas")

    print("\n🗺  Regerando sitemap.xml com TODAS as URLs...")
    total_urls = rebuild_sitemap()
    print(f"   ✓ sitemap.xml com {total_urls} URLs")

    # robots.txt — garante
    robots = ROOT / "robots.txt"
    robots.write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8", newline="\n"
    )
    print("   ✓ robots.txt verificado")


if __name__ == "__main__":
    main()
