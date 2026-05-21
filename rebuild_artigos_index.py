# -*- coding: utf-8 -*-
"""
Reconstroi /artigos/index.html como uma lista ESTATICA de TODOS os artigos.

Atual: usa JS pra renderizar a partir de um JSON embutido. Googlebot
nem sempre executa JS em sites novos, entao os 1351 links viram invisiveis
pro crawler — e nenhum artigo foi descoberto a partir do index.

Novo: lista HTML estatica, com <a href> reais agrupada por inicial.
Mantem todo o head, banner, schema e footer existentes.
"""
import re
from pathlib import Path
from html import escape

ARTIGOS = Path('artigos')


def get_title(html_path):
    text = html_path.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'<title>([^<]+)</title>', text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', text, re.I)
    if m:
        return m.group(1).strip()
    return html_path.stem


def normalize_letter(c):
    c = c.upper()
    if c in 'ÁÀÂÃÄ': return 'A'
    if c in 'ÉÈÊË': return 'E'
    if c in 'ÍÌÎÏ': return 'I'
    if c in 'ÓÒÔÕÖ': return 'O'
    if c in 'ÚÙÛÜ': return 'U'
    if c == 'Ç': return 'C'
    if not c.isalpha(): return '#'
    return c


def collect_articles():
    articles = []
    for f in sorted(ARTIGOS.glob('*.html')):
        if f.name == 'index.html':
            continue
        title = get_title(f)
        slug = f.stem
        articles.append((title, slug))
    return articles


def group_by_letter(articles):
    groups = {}
    for title, slug in articles:
        first = normalize_letter(title[0]) if title else '#'
        groups.setdefault(first, []).append((title, slug))
    # ordena os artigos em cada letra
    for letter in groups:
        groups[letter].sort(key=lambda x: x[0].lower())
    return groups


def build_list_html(articles):
    groups = group_by_letter(articles)
    letters = sorted(groups.keys(), key=lambda x: (x == '#', x))

    letter_nav = '\n'.join(
        f'      <a href="#letter-{l}" style="display:inline-block;padding:6px 10px;margin:2px;'
        f'background:#eef2ff;color:#4F46E5;border-radius:6px;text-decoration:none;'
        f'font-weight:700;font-size:0.9rem">{l}</a>'
        for l in letters
    )

    sections = []
    for letter in letters:
        items = groups[letter]
        lis = '\n'.join(
            f'    <li style="margin:8px 0;padding:8px 0;border-bottom:1px solid #f1f5f9">'
            f'<a href="{escape(slug)}.html" rel="dofollow" '
            f'style="color:#1a1a2e;text-decoration:none;font-weight:500;display:block">'
            f'{escape(title)}</a></li>'
            for title, slug in items
        )
        sections.append(
            f'<section id="letter-{letter}" style="margin:30px 0">\n'
            f'  <h2 style="font-size:1.6rem;color:#4F46E5;border-bottom:2px solid #eef2ff;'
            f'padding-bottom:8px">{letter} <span style="font-size:0.95rem;color:#94a3b8;'
            f'font-weight:500">({len(items)} artigos)</span></h2>\n'
            f'  <ul style="list-style:none;padding:0;margin:0">\n{lis}\n  </ul>\n'
            f'</section>'
        )

    return (
        f'<div class="grid" id="blogGrid">\n'
        f'  <div style="background:#eef2ff;padding:18px;border-radius:12px;margin:20px 0;'
        f'text-align:center">\n'
        f'    <strong style="display:block;margin-bottom:10px;color:#4F46E5;font-size:1.05rem">'
        f'Navegue por letra ({len(articles)} artigos):</strong>\n'
        f'    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px">\n'
        f'{letter_nav}\n'
        f'    </div>\n'
        f'  </div>\n'
        + '\n'.join(sections)
        + '\n</div>'
    )


def main():
    articles = collect_articles()
    print(f'Coletados {len(articles)} artigos')

    index = Path('artigos/index.html')
    raw = index.read_bytes()
    content = raw.decode('utf-8')

    new_list_html = build_list_html(articles)

    # Substitui o bloco dinamico (grid + pagination + script) por HTML estatico.
    pattern = re.compile(
        r'<div class="grid" id="blogGrid"></div>\s*'
        r'<div class="pagination" id="pagination"></div>\s*'
        r'<script>.*?</script>',
        re.DOTALL,
    )

    if not pattern.search(content):
        print('ERRO: padrao do blog dinamico nao encontrado em artigos/index.html')
        return

    new_content = pattern.sub(new_list_html, content)

    new_content = re.sub(
        r'<title>[^<]*</title>',
        f'<title>Todos os Artigos - {len(articles)} guias pedagogicos | Plano de Aula Pronto</title>',
        new_content,
        count=1,
    )
    new_content = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="Indice completo de {len(articles)} '
        f'artigos sobre planos de aula, BNCC, alfabetizacao, atividades e pratica docente. '
        f'Navegue por letra alfabetica."',
        new_content,
        count=1,
    )

    # OG e Twitter
    new_content = re.sub(
        r'(<meta property="og:title" content=")[^"]*(")',
        rf'\1Todos os Artigos - {len(articles)} guias pedagogicos\2',
        new_content,
        count=1,
    )
    new_content = re.sub(
        r'(<meta name="twitter:title" content=")[^"]*(")',
        rf'\1Todos os Artigos - {len(articles)} guias pedagogicos\2',
        new_content,
        count=1,
    )

    index.write_bytes(new_content.encode('utf-8'))
    print(f'Escrito {index}: {len(articles)} artigos como HTML estatico')


if __name__ == '__main__':
    main()
