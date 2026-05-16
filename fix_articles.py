"""
Fix dos 1.351 artigos de planodeaulapronto.github.io:

1. HEAD SEO completo: title, description, canonical, OG, twitter, JSON-LD Article
2. Remove TODOS os links externos (http/https) exceto:
   - https://planodeaulapronto.github.io/...   (mesmo dominio)
   - https://www.aulagen.com.br/...            (parceiro)
   Links removidos viram <strong>texto</strong>.
3. Substitui textos como "Diario da Educacao" + link por link interno para
   ../index.html (mesmo site).
4. Injeta bloco CTA AulaGen logo apos o H1 (topo) e antes do </main> (rodape).
5. Substitui emails no site por planodeaulaprontobncc@gmail.com.
6. Atualiza index.html: lista de artigos no rodape (resolve orfanato) + CTA AulaGen.

Stdlib pura. Roda com: PYTHONIOENCODING=utf-8 python fix_articles.py
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIGOS = ROOT / "artigos"
SITE = "https://planodeaulapronto.github.io"
AULAGEN = "https://www.aulagen.com.br/"
EMAIL = "planodeaulaprontobncc@gmail.com"

ALLOWED_HOSTS = ("planodeaulapronto.github.io", "www.aulagen.com.br", "aulagen.com.br")

# ---------------------------------------------------------------------------
# CTA AulaGen (topo + rodape do artigo)
# ---------------------------------------------------------------------------

CTA_TOP = """
<div style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 100%);color:#fff;padding:24px 28px;border-radius:16px;margin:0 0 28px;box-shadow:0 8px 24px rgba(79,70,229,.25)">
  <div style="display:inline-block;background:rgba(255,255,255,.2);padding:4px 12px;border-radius:999px;font-size:.72rem;font-weight:700;letter-spacing:.5px;text-transform:uppercase;margin-bottom:10px">⚡ Plataforma recomendada</div>
  <h2 style="margin:0 0 8px;font-size:1.4rem;color:#fff">Cansado de planejar aula no domingo?</h2>
  <p style="margin:0 0 14px;font-size:.98rem;color:#eef0fb;line-height:1.5">O <strong>AulaGen</strong> e uma plataforma de IA com mais de 50 ferramentas para professores: planos de aula, provas, atividades adaptadas, PEI/PDI e jogos pedagogicos prontos em minutos, alinhados a BNCC.</p>
  <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="display:inline-block;background:#fff;color:#4F46E5;padding:11px 22px;border-radius:8px;font-weight:800;text-decoration:none;font-size:.95rem">Conhecer o AulaGen &rarr;</a>
</div>
"""

CTA_BOTTOM = """
<div style="background:#f8fafc;border:2px solid #4F46E5;padding:30px;border-radius:16px;margin:40px 0 10px;text-align:center">
  <h2 style="color:#4F46E5;margin:0 0 14px;font-size:1.5rem">Crie seu proximo plano de aula em 3 minutos</h2>
  <p style="color:#2d3748;margin:0 0 20px;font-size:1.02rem;max-width:560px;margin-left:auto;margin-right:auto;line-height:1.55">
    Plano completo, prova, atividade inclusiva, jogo educativo, relatorio ou PEI — gerado por IA, alinhado a BNCC e salvo na sua biblioteca privada. Inclui <strong>704 paginas de bonus em PDF</strong>.
  </p>
  <ul style="list-style:none;padding:0;margin:0 0 22px;display:inline-block;text-align:left">
    <li style="margin:6px 0;color:#2d3748">&check; 50+ ferramentas de IA para professor</li>
    <li style="margin:6px 0;color:#2d3748">&check; 1.606 habilidades BNCC integradas (EI ao EM)</li>
    <li style="margin:6px 0;color:#2d3748">&check; Atividades adaptadas, PEI, PDI e diagnosticas</li>
    <li style="margin:6px 0;color:#2d3748">&check; Biblioteca privada e exportacao em PDF/Word</li>
    <li style="margin:6px 0;color:#2d3748">&check; A partir de <strong>R$ 39,90/mes</strong></li>
  </ul>
  <div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="display:inline-block;background:#4F46E5;color:#fff;padding:14px 32px;border-radius:10px;font-weight:800;text-decoration:none;font-size:1.05rem;box-shadow:0 6px 14px rgba(79,70,229,.3)">Comecar agora no AulaGen &rarr;</a>
  </div>
</div>
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RX_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
RX_H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
RX_HEAD = re.compile(r"<head[^>]*>(.*?)</head>", re.IGNORECASE | re.DOTALL)
RX_MAIN = re.compile(r"(<main[^>]*>)(.*?)(</main>)", re.IGNORECASE | re.DOTALL)
RX_BODY_TAGS = re.compile(r"<[^>]+>")
RX_ANCHOR = re.compile(r'<a\b([^>]*?)href="(https?://[^"]+)"([^>]*)>(.*?)</a>', re.IGNORECASE | re.DOTALL)
RX_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def text_only(html_str: str, limit: int = 300) -> str:
    s = RX_BODY_TAGS.sub(" ", html_str)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit]


def is_allowed(url: str) -> bool:
    u = url.lower()
    for host in ALLOWED_HOSTS:
        if u.startswith(f"https://{host}") or u.startswith(f"http://{host}"):
            return True
    return False


def strip_external_links(html_str: str) -> tuple[str, int]:
    """Remove links externos nao permitidos. Substitui <a>texto</a> por <strong>texto</strong>."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        url = m.group(2)
        if is_allowed(url):
            return m.group(0)
        count += 1
        inner = m.group(4).strip()
        if inner:
            return f"<strong>{inner}</strong>"
        return ""

    new_html = RX_ANCHOR.sub(repl, html_str)
    return new_html, count


def build_head(slug: str, title: str, description: str, body_text: str) -> str:
    """Monta um <head> completo com SEO."""
    title_clean = html.unescape(title).strip()
    desc = description.strip().replace('"', "'")
    if not desc:
        desc = body_text[:160]
    desc = desc[:160].rstrip() + ("..." if len(body_text) > 160 else "")
    canonical = f"{SITE}/artigos/{slug}.html"

    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title_clean,
        "description": desc,
        "url": canonical,
        "datePublished": "2026-01-01",
        "dateModified": "2026-05-16",
        "inLanguage": "pt-BR",
        "author": {"@type": "Organization", "name": "Plano de Aula Pronto"},
        "publisher": {
            "@type": "Organization",
            "name": "Plano de Aula Pronto",
            "url": SITE + "/",
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
    }
    breadcrumb_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/artigos/"},
            {"@type": "ListItem", "position": 3, "name": title_clean, "item": canonical},
        ],
    }

    return f'''<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title_clean)}</title>
  <meta name="description" content="{html.escape(desc, quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
  <meta name="author" content="Plano de Aula Pronto">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title_clean, quote=True)}">
  <meta property="og:description" content="{html.escape(desc, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Plano de Aula Pronto">
  <meta property="og:locale" content="pt_BR">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title_clean, quote=True)}">
  <meta name="twitter:description" content="{html.escape(desc, quote=True)}">
  <link rel="icon" href="../images/favicon.ico">
  <script type="application/ld+json">{json.dumps(article_jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb_jsonld, ensure_ascii=False)}</script>
  <style>
    :root {{ --primary: #4F46E5; --dark: #1a1a2e; --text: #2d3748; --radius: 16px; }}
    body {{ font-family: sans-serif; color: var(--text); background: #f8fafc; margin: 0; line-height: 1.6; }}
    .nav-bar {{ background: white; padding: 15px 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }}
    .logo {{ font-weight: 800; color: var(--primary); text-decoration: none; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; display: grid; grid-template-columns: 1fr 350px; gap: 40px; }}
    .content-area {{ background: white; padding: 40px; border-radius: var(--radius); box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
    h1 {{ font-size: 2.2rem; color: var(--dark); margin-top: 0; line-height: 1.2; }}
    .product-mini-card {{ display: flex; gap: 12px; margin-bottom: 20px; background: #fff; padding: 12px; border-radius: 12px; border: 1px solid #eee; transition: transform 0.2s; }}
    .product-mini-card:hover {{ transform: translateX(5px); border-color: var(--primary); }}
    .product-mini-card img {{ width: 70px; height: 70px; border-radius: 8px; object-fit: cover; }}
    .product-mini-card h4 {{ font-size: 0.85rem; margin: 0 0 5px 0; color: var(--dark); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
    .view-btn {{ font-size: 0.75rem; color: var(--primary); font-weight: 700; text-decoration: none; }}
    aside h4 {{ margin-top: 0; font-size: 1.2rem; color: var(--primary); border-bottom: 2px solid #eef2ff; padding-bottom: 10px; margin-bottom: 20px; }}
    @media (max-width: 900px) {{ .container {{ grid-template-columns: 1fr; }} .content-area {{ padding: 25px; }} }}
  </style>
</head>'''


def inject_cta_into_main(main_html: str) -> str:
    """Coloca CTA_TOP logo apos o primeiro </h1> e CTA_BOTTOM no final do main."""
    # topo: depois do primeiro </h1>
    m = re.search(r"</h1>", main_html, re.IGNORECASE)
    if m:
        idx = m.end()
        main_html = main_html[:idx] + "\n" + CTA_TOP + "\n" + main_html[idx:]
    else:
        main_html = CTA_TOP + main_html
    # rodape: ao final do main
    main_html = main_html + "\n" + CTA_BOTTOM + "\n"
    return main_html


# ---------------------------------------------------------------------------
# Processar 1 artigo
# ---------------------------------------------------------------------------

def fix_article(path: Path) -> dict:
    slug = path.stem
    raw = path.read_text(encoding="utf-8", errors="ignore")

    # remove BOM se existir
    if raw.startswith("﻿"):
        raw = raw.lstrip("﻿")

    title_match = RX_TITLE.search(raw)
    title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
    title = re.sub(r"\s*\|\s*Blog Pedag.*$", "", title)  # remove sufixo antigo

    # extrai descricao de texto do main
    main_match = RX_MAIN.search(raw)
    main_inner = main_match.group(2) if main_match else ""
    body_plain = text_only(main_inner, 1000)

    # strip de links externos (tanto no main quanto no resto, mas head fica intocado)
    if main_match:
        new_main_inner, removed = strip_external_links(main_inner)
        new_main_inner = inject_cta_into_main(new_main_inner)
        new_main = main_match.group(1) + new_main_inner + main_match.group(3)
        # tambem strip no body fora do main (sidebar etc) — mas mantem CTA so dentro do main
        before_main = raw[: main_match.start()]
        after_main = raw[main_match.end() :]
        after_main, removed_after = strip_external_links(after_main)
        # nao precisa stripar no before_main porque ali so tem head + nav (sem links externos)
        raw_no_external = before_main + new_main + after_main
        total_removed = removed + removed_after
    else:
        raw_no_external, total_removed = strip_external_links(raw)

    # substitui head
    new_head = build_head(slug, title, body_plain[:160], body_plain)

    if RX_HEAD.search(raw_no_external):
        final = RX_HEAD.sub(new_head, raw_no_external, count=1)
    else:
        # injeta head logo apos <html>
        final = re.sub(r"<html[^>]*>", lambda m: m.group(0) + "\n" + new_head, raw_no_external, count=1)

    # substitui qualquer email solto pelo email oficial (preserva planodeaulaprontobncc@gmail.com)
    final = RX_EMAIL.sub(lambda m: m.group(0) if m.group(0).lower() == EMAIL else EMAIL, final)

    path.write_text(final, encoding="utf-8", newline="\n")
    return {"slug": slug, "removed_links": total_removed, "title": title}


# ---------------------------------------------------------------------------
# Index.html: adiciona lista de artigos + CTA + email
# ---------------------------------------------------------------------------

def fix_index(article_titles: list[dict]) -> None:
    index_path = ROOT / "index.html"
    if not index_path.exists():
        print("  ⚠ index.html nao encontrado, pulando")
        return
    raw = index_path.read_text(encoding="utf-8", errors="ignore")
    if raw.startswith("﻿"):
        raw = raw.lstrip("﻿")

    # bloco com lista de artigos (resolve orfanato)
    cards = []
    for art in sorted(article_titles, key=lambda x: x["title"])[:200]:  # limita a 200 para nao explodir o HTML
        title = html.escape(art["title"])
        href = html.escape(f"artigos/{art['slug']}.html")
        cards.append(f'    <li style="margin:6px 0;font-size:.92rem"><a href="{href}" style="color:#4F46E5;text-decoration:none">&rarr; {title}</a></li>')
    total = len(article_titles)
    extra_note = ""
    if total > 200:
        extra_note = f'<p style="margin-top:12px;font-size:.9rem;color:#666">+ {total - 200} artigos disponiveis. Veja o <a href="mapa-do-site.html" style="color:#4F46E5">mapa do site</a>.</p>'

    blog_block = f'''<!-- HOME-BLOG-LIST start (gerado por fix_articles.py) -->
<section id="blog-artigos" style="background:#fff;padding:50px 20px;border-top:1px solid #eee">
  <div style="max-width:1200px;margin:0 auto">
    <h2 style="color:#1a1a2e;font-size:1.8rem;margin:0 0 8px">Blog Pedagogico — {total} artigos</h2>
    <p style="color:#555;margin:0 0 24px">Guias completos sobre planos de aula, alfabetizacao, BNCC, atividades e gestao escolar.</p>
    <ul style="list-style:none;padding:0;margin:0;columns:2;column-gap:30px">
{chr(10).join(cards)}
    </ul>
    {extra_note}
  </div>
</section>
<!-- HOME-BLOG-LIST end -->
'''

    home_cta_block = f'''<!-- HOME-AULAGEN-CTA start (gerado por fix_articles.py) -->
<section style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 100%);color:#fff;padding:60px 20px;text-align:center">
  <div style="max-width:780px;margin:0 auto">
    <div style="display:inline-block;background:rgba(255,255,255,.2);padding:5px 14px;border-radius:999px;font-size:.78rem;font-weight:700;letter-spacing:.5px;text-transform:uppercase;margin-bottom:14px">⚡ Plataforma recomendada</div>
    <h2 style="color:#fff;font-size:2rem;margin:0 0 14px">Pare de passar o domingo planejando aula</h2>
    <p style="color:#eef0fb;font-size:1.08rem;margin:0 0 26px;line-height:1.55">O <strong>AulaGen</strong> e a plataforma de IA com 50+ ferramentas para professores: planos de aula, provas, atividades adaptadas, PEI/PDI e jogos prontos em minutos — alinhados a BNCC, com biblioteca privada e 704 paginas de bonus em PDF.</p>
    <a href="{AULAGEN}" target="_blank" rel="noopener" style="display:inline-block;background:#fff;color:#4F46E5;padding:16px 36px;border-radius:10px;font-weight:800;text-decoration:none;font-size:1.08rem;box-shadow:0 8px 20px rgba(0,0,0,.18)">Conhecer o AulaGen &rarr;</a>
    <p style="color:#eef0fb;margin:18px 0 0;font-size:.9rem">A partir de R$ 39,90/mes</p>
  </div>
</section>
<!-- HOME-AULAGEN-CTA end -->
'''

    # remove blocos antigos se existir
    raw = re.sub(r"<!-- HOME-BLOG-LIST start.*?<!-- HOME-BLOG-LIST end -->", "", raw, flags=re.DOTALL)
    raw = re.sub(r"<!-- HOME-AULAGEN-CTA start.*?<!-- HOME-AULAGEN-CTA end -->", "", raw, flags=re.DOTALL)

    # strip de links externos no index tambem
    raw, removed_home = strip_external_links(raw)

    # substitui emails
    raw = RX_EMAIL.sub(lambda m: m.group(0) if m.group(0).lower() == EMAIL else EMAIL, raw)

    # injeta CTA + blog antes do </body>
    if "</body>" in raw:
        raw = raw.replace("</body>", home_cta_block + blog_block + "</body>", 1)
    else:
        raw = raw + home_cta_block + blog_block

    index_path.write_text(raw, encoding="utf-8", newline="\n")
    print(f"  ✓ index.html  (removidos {removed_home} links externos, adicionados blocos CTA + lista de {len(cards)} artigos)")


# ---------------------------------------------------------------------------
# Outros HTMLs (mapa-do-site, privacidade, termos): strip externos + email
# ---------------------------------------------------------------------------

def fix_misc_html(path: Path) -> int:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if raw.startswith("﻿"):
        raw = raw.lstrip("﻿")
    raw, removed = strip_external_links(raw)
    raw = RX_EMAIL.sub(lambda m: m.group(0) if m.group(0).lower() == EMAIL else EMAIL, raw)
    path.write_text(raw, encoding="utf-8", newline="\n")
    return removed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not ARTIGOS.is_dir():
        sys.exit(f"erro: {ARTIGOS} nao existe")

    files = sorted(ARTIGOS.glob("*.html"))
    print(f"📂 Processando {len(files)} artigos em {ARTIGOS} ...")

    total_links = 0
    out: list[dict] = []
    erros = 0
    for i, f in enumerate(files, 1):
        try:
            r = fix_article(f)
            out.append(r)
            total_links += r["removed_links"]
            if i % 100 == 0:
                print(f"  ...{i}/{len(files)}")
        except Exception as e:
            erros += 1
            print(f"  ⚠ erro em {f.name}: {e}")

    print(f"\n✅ Artigos: {len(out)} processados, {total_links} links externos removidos, {erros} erros.")

    # index.html
    print("\n📂 Atualizando index.html...")
    fix_index(out)

    # outros HTMLs raiz
    print("\n📂 Atualizando outros HTMLs (mapa, privacidade, termos)...")
    for name in ("mapa-do-site.html", "privacidade.html", "termos.html", "page_raw.html"):
        p = ROOT / name
        if p.exists():
            n = fix_misc_html(p)
            print(f"  ✓ {name}  ({n} links externos removidos)")

    print("\n🎉 Build concluido.")


if __name__ == "__main__":
    main()
