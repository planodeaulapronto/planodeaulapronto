# -*- coding: utf-8 -*-
"""
Cria /produto/index.html como hub estatico listando os 438 produtos
(de /produto/ e /produtos/). Modelado no estilo de artigos/index.html:
- Cabecalho com banner AulaGen
- Schema.org
- Lista estatica com TODOS os produtos
- Footer padrao
"""
import re
from pathlib import Path
from html import escape

ROOT = Path('.')


def get_title(html_path):
    try:
        text = html_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return html_path.stem
    m = re.search(r'<title>([^<|]+)', text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', text, re.I)
    if m:
        return m.group(1).strip()
    return html_path.stem


def collect_produtos():
    items = []
    for d in ('produto', 'produtos'):
        for f in (ROOT / d).glob('*.html'):
            if f.name == 'index.html':
                continue
            items.append((get_title(f), f'../{d}/{f.stem}.html'))
    return sorted(items, key=lambda x: x[0].lower())


BANNER = '''<!-- AULAGEN-STICKY-BANNER start -->
<div id="aulagen-sticky-banner" style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 52%,#ec4899 100%);color:#fff;padding:12px 18px;position:sticky;top:0;z-index:9999;box-shadow:0 2px 14px rgba(0,0,0,.2);font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
    <div style="display:flex;align-items:center;gap:12px;flex:1;min-width:250px">
      <div style="background:rgba(255,255,255,.2);width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;line-height:1;flex:0 0 38px">🤖</div>
      <div style="line-height:1.28;min-width:0">
        <div style="font-weight:850;font-size:.98rem;white-space:normal">AulaGen — IA para Professores</div>
        <div style="font-size:.82rem;opacity:.94;white-space:normal">Planos, provas, atividades adaptadas e simulados de concursos em minutos.</div>
      </div>
    </div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="background:#fff;color:#4F46E5;padding:9px 18px;border-radius:7px;font-weight:850;text-decoration:none;font-size:.86rem;white-space:nowrap;box-shadow:0 4px 10px rgba(0,0,0,.15);flex-shrink:0">Conhecer →</a>
  </div>
</div>
<!-- AULAGEN-STICKY-BANNER end -->'''


def build_html(produtos):
    n = len(produtos)
    today = '2026-05-20'

    schema = (
        '{"@context":"https://schema.org","@graph":['
        '{"@type":"WebSite","@id":"https://planodeaulapronto.github.io/#website",'
        '"url":"https://planodeaulapronto.github.io/","name":"Plano de Aula Pronto",'
        '"inLanguage":"pt-BR"},'
        '{"@type":"CollectionPage","@id":"https://planodeaulapronto.github.io/produto/index.html#webpage",'
        '"url":"https://planodeaulapronto.github.io/produto/index.html",'
        f'"name":"Todos os Produtos - {n} materiais pedagogicos BNCC 2026",'
        f'"description":"Catalogo completo de {n} planos de aula, atividades, avaliacoes e materiais pedagogicos alinhados a BNCC 2026.",'
        '"inLanguage":"pt-BR",'
        '"isPartOf":{"@id":"https://planodeaulapronto.github.io/#website"}},'
        '{"@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Inicio","item":"https://planodeaulapronto.github.io/"},'
        f'{{"@type":"ListItem","position":2,"name":"Produtos","item":"https://planodeaulapronto.github.io/produto/index.html"}}'
        ']}'
        ']}'
    )

    items_html = '\n'.join(
        f'    <li style="margin:8px 0;padding:12px;background:#fff;border:1px solid #eef2ff;border-radius:10px">'
        f'<a href="{escape(href)}" rel="dofollow" '
        f'style="color:#1a1a2e;text-decoration:none;font-weight:500;display:block;font-size:0.9rem;line-height:1.4">'
        f'{escape(title)}</a></li>'
        for title, href in produtos
    )

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todos os Produtos - {n} materiais BNCC 2026 | Plano de Aula Pronto</title>
  <meta name="description" content="Catalogo completo de {n} planos de aula, atividades, avaliacoes e slides alinhados a BNCC 2026. Educacao Infantil, Fundamental e Ensino Medio.">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
  <link rel="canonical" href="https://planodeaulapronto.github.io/produto/index.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Todos os Produtos - {n} materiais BNCC 2026">
  <meta property="og:url" content="https://planodeaulapronto.github.io/produto/index.html">
  <meta property="og:site_name" content="Plano de Aula Pronto">
  <meta property="og:locale" content="pt_BR">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Todos os Produtos - {n} materiais BNCC 2026">
  <link rel="icon" href="../images/favicon.ico">
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; color: #2d3748; background: #f8fafc; margin: 0; line-height: 1.5; }}
    .nav-bar {{ background: white; padding: 15px 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); display: flex; justify-content: space-between; align-items: center; }}
    .logo {{ font-weight: 800; color: #4F46E5; text-decoration: none; font-size: 1.2rem; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
    h1 {{ font-size: 2rem; color: #1a1a2e; margin-top: 0; }}
    h2 {{ font-size: 1.4rem; color: #4F46E5; border-bottom: 2px solid #eef2ff; padding-bottom: 8px; margin-top: 30px; }}
    ul.grid {{ list-style: none; padding: 0; margin: 20px 0; column-count: 2; column-gap: 20px; }}
    @media (max-width: 720px) {{ ul.grid {{ column-count: 1; }} }}
  </style>
<script type="application/ld+json">{schema}</script>
</head>
<body>
{BANNER}
<nav class="nav-bar">
  <a href="../index.html" class="logo">📚 Plano de Aula Pronto</a>
  <div>
    <a href="../index.html" style="color:#2d3748;text-decoration:none;margin-right:14px">Inicio</a>
    <a href="../artigos/index.html" style="color:#2d3748;text-decoration:none;margin-right:14px">Artigos</a>
    <a href="../cidades/index.html" style="color:#2d3748;text-decoration:none">Concursos</a>
  </div>
</nav>
<div class="container">
  <nav style="font-size:0.85rem;color:#64748b;margin-bottom:16px">
    <a href="../index.html" style="color:#4F46E5;text-decoration:none">Inicio</a> &rsaquo;
    <span>Produtos</span>
  </nav>
  <h1>Todos os Produtos ({n})</h1>
  <p style="color:#64748b;font-size:1.02rem;max-width:780px">
    Catalogo completo de {n} planos de aula prontos, atividades, avaliacoes,
    slides e materiais pedagogicos alinhados a BNCC 2026. Da Educacao Infantil
    ao Ensino Medio, com download imediato apos a compra via Hotmart.
  </p>

  <div style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 100%);color:#fff;padding:20px 24px;border-radius:14px;margin:24px 0">
    <div style="font-weight:800;font-size:1.05rem;margin-bottom:6px">Cansado de planejar aula no domingo?</div>
    <div style="font-size:0.9rem;opacity:0.92;margin-bottom:10px">
      A <strong>AulaGen</strong> gera planos de aula, provas e atividades com IA em minutos. Alinhado a BNCC 2026.
    </div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="display:inline-block;background:#fff;color:#4F46E5;padding:9px 18px;border-radius:7px;font-weight:800;text-decoration:none;font-size:0.85rem">Conhecer o AulaGen &rarr;</a>
  </div>

  <h2 id="materiais">Materiais pedagogicos BNCC</h2>
  <ul class="grid">
{items_html}
  </ul>
</div>
<footer style="background:#1a1a2e;color:white;padding:30px 20px;text-align:center;margin-top:40px">
  <p>&copy; 2026 - <a href="../index.html" style="color:#FFD700;text-decoration:none">Plano de Aula Pronto - Materiais Pedagogicos BNCC 2026</a></p>
  <p style="margin-top:10px;font-size:0.85rem;opacity:0.8">
    <a href="../privacidade.html" style="color:white;margin:0 10px">Politica de Privacidade</a> |
    <a href="../termos.html" style="color:white;margin:0 10px">Termos de Uso</a> |
    <a href="../mapa-do-site.html" style="color:white;margin:0 10px">Mapa do Site</a>
  </p>
</footer>
</body>
</html>
'''


def main():
    produtos = collect_produtos()
    print(f'Coletados {len(produtos)} produtos')
    html = build_html(produtos)

    out1 = Path('produto/index.html')
    out1.write_text(html, encoding='utf-8')
    print(f'Escrito {out1}')

    # Cria produtos/index.html com canonical apontando pro /produto/index.html
    # (mesma listagem, mas com paths ajustados)
    items2 = [(t, f'../produtos/{Path(h).name}' if 'produtos/' in h else f'../produto/{Path(h).name}')
              for t, h in produtos]
    # Mais simples: gera o mesmo HTML mas com canonical para /produto/index.html
    html2 = html.replace(
        'rel="canonical" href="https://planodeaulapronto.github.io/produto/index.html"',
        'rel="canonical" href="https://planodeaulapronto.github.io/produto/index.html"'
    )
    # O paths nos links sao ../produto/X e ../produtos/X — funciona dos dois lugares
    out2 = Path('produtos/index.html')
    out2.write_text(html, encoding='utf-8')
    print(f'Escrito {out2} (canonical aponta pro /produto/index.html)')


if __name__ == '__main__':
    main()
