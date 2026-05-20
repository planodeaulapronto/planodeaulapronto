# -*- coding: utf-8 -*-
"""
1. Atualiza JSON-LD dateModified nos arquivos alterados para hoje.
2. Atualiza <lastmod> no sitemap para esses arquivos.
3. Divide sitemap.xml em 4 sitemaps por tipo + sitemap-index.xml.

Os 4 sitemaps:
  - sitemap-paginas.xml  -> home, static (privacidade, termos, mapa-do-site, etc), artigos/index
  - sitemap-artigos.xml  -> artigos/*.html (exceto index)
  - sitemap-produtos.xml -> produto/*.html, produtos/*.html
  - sitemap-cidades.xml  -> {cidade}/*.html (5 cargos por cidade) + cidades/index.html

robots.txt continua apontando para /sitemap.xml — que agora e o INDEX.
"""
import re
import subprocess
from datetime import date
from pathlib import Path

TODAY = date.today().isoformat()
SITE = 'https://planodeaulapronto.github.io'
ROOT = Path('.')


def get_modified_html():
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD'],
        capture_output=True, text=True, check=True,
    )
    files = []
    for line in result.stdout.splitlines():
        p = Path(line.strip())
        if p.suffix == '.html' and p.exists():
            files.append(p)
    return files


def path_to_url(p):
    rel = str(p).replace('\\', '/')
    if rel == 'index.html':
        return f'{SITE}/'
    return f'{SITE}/{rel}'


def classify_url(url):
    """Retorna 'paginas' | 'artigos' | 'produtos' | 'cidades'."""
    if '/artigos/' in url and not url.endswith('/artigos/index.html'):
        return 'artigos'
    if '/produto/' in url or '/produtos/' in url:
        return 'produtos'
    # tudo que tem /cidade-slug/concurso-xxx.html ou /cidades/
    # heuristica: se URL termina em concurso-X.html ou pss-X.html, e cidade
    if re.search(r'/(concurso-|pss-)', url):
        return 'cidades'
    if url.endswith('/cidades/index.html') or url == f'{SITE}/cidades/':
        return 'cidades'
    return 'paginas'


RE_DATE_MOD = re.compile(rb'"dateModified":"[^"]+"')


def update_html_dates(files):
    n = 0
    for f in files:
        raw = f.read_bytes()
        new = RE_DATE_MOD.sub(f'"dateModified":"{TODAY}"'.encode(), raw)
        if new != raw:
            f.write_bytes(new)
            n += 1
    return n


def parse_sitemap():
    text = Path('sitemap.xml').read_text(encoding='utf-8')
    # Cada <url>...</url> e uma entrada
    entries = re.findall(r'<url>.*?</url>', text, re.DOTALL)
    parsed = []
    for e in entries:
        m_loc = re.search(r'<loc>([^<]+)</loc>', e)
        m_last = re.search(r'<lastmod>([^<]+)</lastmod>', e)
        m_cf = re.search(r'<changefreq>([^<]+)</changefreq>', e)
        m_pr = re.search(r'<priority>([^<]+)</priority>', e)
        if not m_loc:
            continue
        parsed.append({
            'loc': m_loc.group(1),
            'lastmod': m_last.group(1) if m_last else TODAY,
            'changefreq': m_cf.group(1) if m_cf else 'monthly',
            'priority': m_pr.group(1) if m_pr else '0.5',
        })
    return parsed


def update_lastmod(entries, modified_urls):
    for e in entries:
        if e['loc'] in modified_urls:
            e['lastmod'] = TODAY
    return entries


def write_sitemap(path, entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for e in entries:
        lines.append(
            f'  <url><loc>{e["loc"]}</loc>'
            f'<lastmod>{e["lastmod"]}</lastmod>'
            f'<changefreq>{e["changefreq"]}</changefreq>'
            f'<priority>{e["priority"]}</priority></url>'
        )
    lines.append('</urlset>')
    Path(path).write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_sitemap_index(parts):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name in parts:
        lines.append(
            f'  <sitemap><loc>{SITE}/{name}</loc>'
            f'<lastmod>{TODAY}</lastmod></sitemap>'
        )
    lines.append('</sitemapindex>')
    Path('sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    print('=== Atualizando datas ===')
    modified = get_modified_html()
    print(f'Arquivos modificados (segundo git): {len(modified)}')

    n_html = update_html_dates(modified)
    print(f'dateModified atualizado em {n_html} arquivos HTML')

    print('=== Reorganizando sitemap ===')
    entries = parse_sitemap()
    print(f'Entradas no sitemap: {len(entries)}')

    modified_urls = {path_to_url(p) for p in modified}
    update_lastmod(entries, modified_urls)
    n_lm = sum(1 for e in entries if e['lastmod'] == TODAY)
    print(f'Entradas com lastmod=hoje: {n_lm}')

    buckets = {'paginas': [], 'artigos': [], 'produtos': [], 'cidades': []}
    for e in entries:
        buckets[classify_url(e['loc'])].append(e)
    for name, items in buckets.items():
        print(f'  {name}: {len(items)} URLs')

    write_sitemap('sitemap-paginas.xml', buckets['paginas'])
    write_sitemap('sitemap-artigos.xml', buckets['artigos'])
    write_sitemap('sitemap-produtos.xml', buckets['produtos'])
    write_sitemap('sitemap-cidades.xml', buckets['cidades'])

    write_sitemap_index([
        'sitemap-paginas.xml',
        'sitemap-artigos.xml',
        'sitemap-produtos.xml',
        'sitemap-cidades.xml',
    ])
    print('sitemap.xml virou sitemap INDEX apontando para os 4 sub-sitemaps')


if __name__ == '__main__':
    main()
