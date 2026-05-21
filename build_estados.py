# -*- coding: utf-8 -*-
"""
Cria paginas-hub por estado: /sp/index.html, /mg/index.html, etc.
Cada uma lista as cidades daquele UF com os 5 cargos.

Adiciona ao sitemap-paginas.xml automaticamente.
"""
import json
import re
from pathlib import Path
from html import escape
from unicodedata import normalize

ROOT = Path('.')
TODAY = '2026-05-20'

CARGOS = [
    ('concurso-professor.html', 'Professor'),
    ('concurso-pedagogo.html', 'Pedagogo'),
    ('pss-professor.html', 'Professor PSS'),
    ('concurso-educacao-infantil.html', 'Educacao Infantil'),
    ('concurso-auxiliar-educacao-infantil.html', 'Auxiliar Educacao Infantil'),
]


def slugify(name):
    s = normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii').lower()
    s = re.sub(r"[^a-z0-9]+", '-', s).strip('-')
    return s


def load_uf_map():
    """Retorna dict slug -> (cidade_nome, UF_sigla, UF_nome, regiao)."""
    data = json.loads(Path('ibge_municipios.json').read_text(encoding='utf-8'))
    out = {}
    for m in data:
        nome = m['nome']
        slug = slugify(nome)
        uf = None
        # Caminho 1: microrregiao
        micro = m.get('microrregiao')
        if micro and micro.get('mesorregiao'):
            uf = micro['mesorregiao'].get('UF')
        # Caminho 2: regiao-imediata (fallback)
        if not uf:
            imed = m.get('regiao-imediata')
            if imed and imed.get('regiao-intermediaria'):
                uf = imed['regiao-intermediaria'].get('UF')
        if not uf:
            continue
        out[slug] = {
            'nome': nome,
            'uf': uf['sigla'],
            'uf_nome': uf['nome'],
            'regiao': uf['regiao']['nome'],
        }
    return out


def collect_existing_cities():
    """Retorna lista de slugs que tem pelo menos concurso-professor.html local."""
    cities = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        if (d / 'concurso-professor.html').exists():
            cities.append(d.name)
    return cities


BANNER = '''<!-- AULAGEN-STICKY-BANNER start -->
<div id="aulagen-sticky-banner" style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 52%,#ec4899 100%);color:#fff;padding:12px 18px;position:sticky;top:0;z-index:9999;box-shadow:0 2px 14px rgba(0,0,0,.2);font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
    <div style="display:flex;align-items:center;gap:12px;flex:1;min-width:250px">
      <div style="background:rgba(255,255,255,.2);width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;line-height:1;flex:0 0 38px">🤖</div>
      <div style="line-height:1.28;min-width:0">
        <div style="font-weight:850;font-size:.98rem;white-space:normal">AulaGen - IA para Professores</div>
        <div style="font-size:.82rem;opacity:.94;white-space:normal">Planos, provas, atividades adaptadas e simulados de concursos em minutos.</div>
      </div>
    </div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="background:#fff;color:#4F46E5;padding:9px 18px;border-radius:7px;font-weight:850;text-decoration:none;font-size:.86rem;white-space:nowrap;box-shadow:0 4px 10px rgba(0,0,0,.15);flex-shrink:0">Conhecer &rarr;</a>
  </div>
</div>
<!-- AULAGEN-STICKY-BANNER end -->'''


def build_state_page(uf_sigla, uf_nome, regiao, cities):
    n_cities = len(cities)
    n_pages = n_cities * len(CARGOS)

    # Lista de cidades com seus 5 cargos
    city_blocks = []
    for slug, nome in sorted(cities, key=lambda x: x[1].lower()):
        cargos_html = ' &middot; '.join(
            f'<a href="../{escape(slug)}/{file}" rel="dofollow" '
            f'style="color:#4F46E5;text-decoration:none">{escape(label)}</a>'
            for file, label in CARGOS
        )
        city_blocks.append(
            f'  <li style="background:#fff;border:1px solid #eef2ff;border-radius:10px;'
            f'padding:14px 18px;margin-bottom:10px">'
            f'<h3 style="margin:0 0 6px;font-size:1.05rem;color:#1a1a2e">'
            f'<a href="../{escape(slug)}/concurso-professor.html" rel="dofollow" '
            f'style="color:#1a1a2e;text-decoration:none">{escape(nome)}</a></h3>'
            f'<div style="font-size:0.82rem;color:#64748b">{cargos_html}</div></li>'
        )

    schema = (
        '{"@context":"https://schema.org","@graph":['
        '{"@type":"WebSite","@id":"https://planodeaulapronto.github.io/#website",'
        '"url":"https://planodeaulapronto.github.io/","name":"Plano de Aula Pronto","inLanguage":"pt-BR"},'
        f'{{"@type":"CollectionPage","@id":"https://planodeaulapronto.github.io/{uf_sigla.lower()}/index.html#webpage",'
        f'"url":"https://planodeaulapronto.github.io/{uf_sigla.lower()}/index.html",'
        f'"name":"Concursos da Educacao em {escape(uf_nome)} ({uf_sigla})",'
        f'"description":"Concursos publicos da educacao em {escape(uf_nome)}: {n_cities} cidades, {n_pages} paginas com informacoes de professor, pedagogo, educacao infantil e PSS.",'
        '"inLanguage":"pt-BR","isPartOf":{"@id":"https://planodeaulapronto.github.io/#website"}},'
        '{"@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Inicio","item":"https://planodeaulapronto.github.io/"},'
        '{"@type":"ListItem","position":2,"name":"Concursos","item":"https://planodeaulapronto.github.io/cidades/index.html"},'
        f'{{"@type":"ListItem","position":3,"name":"{escape(uf_nome)}","item":"https://planodeaulapronto.github.io/{uf_sigla.lower()}/index.html"}}'
        ']}]}'
    )

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Concursos da Educacao em {escape(uf_nome)} ({uf_sigla}) - {n_cities} cidades | Plano de Aula Pronto</title>
  <meta name="description" content="Concursos publicos da educacao em {escape(uf_nome)}: {n_cities} cidades, materiais para professor, pedagogo, educacao infantil e PSS. Materiais alinhados a BNCC 2026.">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
  <link rel="canonical" href="https://planodeaulapronto.github.io/{uf_sigla.lower()}/index.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Concursos da Educacao em {escape(uf_nome)} ({uf_sigla})">
  <meta property="og:url" content="https://planodeaulapronto.github.io/{uf_sigla.lower()}/index.html">
  <meta property="og:site_name" content="Plano de Aula Pronto">
  <meta property="og:locale" content="pt_BR">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="../images/favicon.ico">
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; color: #2d3748; background: #f8fafc; margin: 0; line-height: 1.5; }}
    .nav-bar {{ background: white; padding: 14px 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); display: flex; justify-content: space-between; align-items: center; }}
    .logo {{ font-weight: 800; color: #4F46E5; text-decoration: none; font-size: 1.15rem; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 20px; }}
    h1 {{ font-size: 1.9rem; color: #1a1a2e; margin-top: 0; }}
    ul.cities {{ list-style: none; padding: 0; margin: 24px 0; column-count: 2; column-gap: 18px; }}
    ul.cities li {{ break-inside: avoid; }}
    @media (max-width: 720px) {{ ul.cities {{ column-count: 1; }} }}
  </style>
<script type="application/ld+json">{schema}</script>
</head>
<body>
{BANNER}
<nav class="nav-bar">
  <a href="../index.html" class="logo">📚 Plano de Aula Pronto</a>
  <div>
    <a href="../index.html" style="color:#2d3748;text-decoration:none;margin-right:14px">Inicio</a>
    <a href="../cidades/index.html" style="color:#2d3748;text-decoration:none;margin-right:14px">Cidades</a>
    <a href="../artigos/index.html" style="color:#2d3748;text-decoration:none">Artigos</a>
  </div>
</nav>
<div class="container">
  <nav style="font-size:0.85rem;color:#64748b;margin-bottom:14px">
    <a href="../index.html" style="color:#4F46E5;text-decoration:none">Inicio</a> &rsaquo;
    <a href="../cidades/index.html" style="color:#4F46E5;text-decoration:none">Concursos</a> &rsaquo;
    <span>{escape(uf_nome)}</span>
  </nav>
  <h1>Concursos da Educacao em {escape(uf_nome)} ({uf_sigla})</h1>
  <p style="color:#64748b;font-size:1rem;max-width:780px">
    {n_cities} cidades de {escape(uf_nome)} ({escape(regiao)}) com materiais e
    informacoes para concursos publicos da educacao. Para cada cidade, ha paginas
    de Professor, Pedagogo, Educacao Infantil, Auxiliar e PSS.
  </p>

  <div style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 100%);color:#fff;padding:18px 22px;border-radius:12px;margin:24px 0">
    <div style="font-weight:800;font-size:1rem;margin-bottom:5px">Estude com IA para o concurso de {escape(uf_nome)}</div>
    <div style="font-size:0.88rem;opacity:0.92;margin-bottom:10px">
      A <strong>AulaGen</strong> gera simulados, questoes comentadas, planos de estudo por edital
      e resumos de legislacao da educacao em minutos.
    </div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="display:inline-block;background:#fff;color:#4F46E5;padding:8px 16px;border-radius:6px;font-weight:800;text-decoration:none;font-size:0.85rem">Conhecer o AulaGen &rarr;</a>
  </div>

  <h2 style="font-size:1.3rem;color:#1a1a2e;border-bottom:2px solid #eef2ff;padding-bottom:8px">Cidades de {escape(uf_nome)} ({n_cities})</h2>
  <ul class="cities">
{chr(10).join(city_blocks)}
  </ul>
</div>
<footer style="background:#1a1a2e;color:white;padding:28px 20px;text-align:center;margin-top:40px">
  <p>&copy; 2026 - <a href="../index.html" style="color:#FFD700;text-decoration:none">Plano de Aula Pronto - Materiais Pedagogicos BNCC 2026</a></p>
  <p style="margin-top:8px;font-size:0.85rem;opacity:0.85">
    <a href="../privacidade.html" style="color:white;margin:0 10px">Politica de Privacidade</a> |
    <a href="../termos.html" style="color:white;margin:0 10px">Termos de Uso</a> |
    <a href="../mapa-do-site.html" style="color:white;margin:0 10px">Mapa do Site</a>
  </p>
</footer>
</body>
</html>
'''


def update_sitemap(uf_siglas):
    p = Path('sitemap-paginas.xml')
    xml = p.read_text(encoding='utf-8')
    new_entries = []
    for sigla in uf_siglas:
        url = f'https://planodeaulapronto.github.io/{sigla.lower()}/index.html'
        if url in xml:
            continue
        new_entries.append(
            f'  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod>'
            f'<changefreq>monthly</changefreq><priority>0.75</priority></url>'
        )
    if new_entries:
        xml = xml.replace('</urlset>', '\n'.join(new_entries) + '\n</urlset>')
        p.write_text(xml, encoding='utf-8')
        print(f'Sitemap-paginas: +{len(new_entries)} entradas')
        # Atualiza .txt
        urls = re.findall(r'<loc>([^<]+)</loc>', xml)
        Path('sitemap-paginas.txt').write_text('\n'.join(urls) + '\n', encoding='utf-8')


def main():
    uf_map = load_uf_map()
    existing = collect_existing_cities()
    print(f'Cidades existentes localmente: {len(existing)}')
    print(f'Slugs no IBGE: {len(uf_map)}')

    # Mapa auxiliar: uf_sigla -> (uf_nome, regiao) (qualquer cidade desse UF serve)
    uf_info = {}
    for info in uf_map.values():
        uf_info[info['uf']] = (info['uf_nome'], info['regiao'])

    UFS = {'ac','al','am','ap','ba','ce','df','es','go','ma','mg','ms','mt',
           'pa','pb','pe','pi','pr','rj','rn','ro','rr','rs','sc','se','sp','to'}

    # Agrupa por UF
    by_uf = {}
    not_matched = []
    for slug in existing:
        info = uf_map.get(slug)
        if not info:
            # Tenta slug com sufixo UF: 'alagoinha-pe' -> base='alagoinha' uf='PE'
            parts = slug.rsplit('-', 1)
            if len(parts) == 2 and parts[1] in UFS:
                base, uf_suffix = parts
                uf_sigla = uf_suffix.upper()
                base_info = uf_map.get(base)
                if base_info and uf_sigla in uf_info:
                    uf_nome, regiao = uf_info[uf_sigla]
                    info = {
                        'nome': base_info['nome'],
                        'uf': uf_sigla,
                        'uf_nome': uf_nome,
                        'regiao': regiao,
                    }
        if info:
            by_uf.setdefault(info['uf'], {
                'uf_nome': info['uf_nome'],
                'regiao': info['regiao'],
                'cities': [],
            })['cities'].append((slug, info['nome']))
        else:
            not_matched.append(slug)

    if not_matched:
        print(f'AVISO: {len(not_matched)} slugs sem match no IBGE (primeiros 5): {not_matched[:5]}')

    print(f'Estados com paginas geradas: {len(by_uf)}')
    for uf, data in sorted(by_uf.items()):
        print(f'  {uf}: {len(data["cities"])} cidades')

    # Gera as paginas
    for uf, data in sorted(by_uf.items()):
        out = Path(uf.lower()) / 'index.html'
        out.parent.mkdir(exist_ok=True)
        html = build_state_page(uf, data['uf_nome'], data['regiao'], data['cities'])
        out.write_text(html, encoding='utf-8')

    # Atualiza sitemap
    update_sitemap(sorted(by_uf.keys()))

    print(f'Total: {len(by_uf)} paginas-hub de estado geradas')


if __name__ == '__main__':
    main()
