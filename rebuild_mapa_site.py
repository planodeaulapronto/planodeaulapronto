# -*- coding: utf-8 -*-
"""
Reconstroi mapa-do-site.html completo:
- TODOS os 1350 artigos (atual tem so 853)
- TODOS os 219 produtos (atual ja tem)
- TODAS as 794 cidades (atual tem 0) - 1 link por cidade pra concurso-professor.html
- Links pras paginas hub: artigos/index, cidades/index, discipline-pages, etc.
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


def collect_artigos():
    return sorted(
        (get_title(f), f.stem)
        for f in (ROOT / 'artigos').glob('*.html')
        if f.name != 'index.html'
    )


def collect_produtos():
    items = []
    for d in ('produto', 'produtos'):
        for f in (ROOT / d).glob('*.html'):
            items.append((get_title(f), f'{d}/{f.stem}'))
    return sorted(items)


def collect_cidades():
    cities = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        # Identifica diretorios de cidade (tem concurso-professor.html dentro)
        if (d / 'concurso-professor.html').exists():
            # Pretty name from slug
            pretty = d.name.replace('-', ' ').title()
            cities.append((pretty, d.name))
    return cities


def make_section(title, items, base_href='', cols=2):
    """Gera secao com lista de links em colunas CSS."""
    lis = '\n'.join(
        f"    <li style='break-inside:avoid;margin-bottom:6px'>"
        f"<a href='{escape(base_href + slug)}' rel='dofollow' "
        f"style='color:#1a1a2e;text-decoration:none;font-size:0.82rem;"
        f"line-height:1.4;display:block'>{escape(t)}</a></li>"
        for t, slug in items
    )
    return (
        f'<h2 id="{re.sub(r"[^a-z]+", "-", title.lower()).strip("-")}">'
        f'{escape(title)} ({len(items)})</h2>\n'
        f'<ul style="list-style:none;padding:0;margin:20px 0;'
        f'column-count:{cols};column-gap:30px">\n{lis}\n</ul>'
    )


def main():
    artigos = collect_artigos()
    produtos = collect_produtos()
    cidades = collect_cidades()
    print(f'Artigos: {len(artigos)}')
    print(f'Produtos: {len(produtos)}')
    print(f'Cidades: {len(cidades)}')

    mapa = Path('mapa-do-site.html')
    raw = mapa.read_bytes()
    content = raw.decode('utf-8')

    new_body = []

    # Secao Hub
    new_body.append(
        '<h2 id="paginas-principais">Paginas Principais</h2>\n'
        '<ul style="list-style:none;padding:0;margin:20px 0;column-count:2;column-gap:30px">\n'
        '    <li style="break-inside:avoid;margin-bottom:6px"><a href="index.html" rel="dofollow" '
        'style="color:#1a1a2e;text-decoration:none;font-size:0.82rem;display:block">'
        'Home - Plano de Aula Pronto BNCC 2026</a></li>\n'
        '    <li style="break-inside:avoid;margin-bottom:6px"><a href="artigos/index.html" rel="dofollow" '
        'style="color:#1a1a2e;text-decoration:none;font-size:0.82rem;display:block">'
        f'Blog Pedagogico - {len(artigos)} artigos</a></li>\n'
        '    <li style="break-inside:avoid;margin-bottom:6px"><a href="cidades/index.html" rel="dofollow" '
        'style="color:#1a1a2e;text-decoration:none;font-size:0.82rem;display:block">'
        f'Concursos por Cidade - {len(cidades)} cidades</a></li>\n'
        '    <li style="break-inside:avoid;margin-bottom:6px"><a href="canva/index.html" rel="dofollow" '
        'style="color:#1a1a2e;text-decoration:none;font-size:0.82rem;display:block">'
        'Materiais Pedagogicos BNCC 2026</a></li>\n'
        '    <li style="break-inside:avoid;margin-bottom:6px"><a href="privacidade.html" rel="dofollow" '
        'style="color:#1a1a2e;text-decoration:none;font-size:0.82rem;display:block">'
        'Politica de Privacidade</a></li>\n'
        '    <li style="break-inside:avoid;margin-bottom:6px"><a href="termos.html" rel="dofollow" '
        'style="color:#1a1a2e;text-decoration:none;font-size:0.82rem;display:block">'
        'Termos de Uso</a></li>\n'
        '</ul>'
    )

    # Discipline pages
    disc_pages = sorted(ROOT.glob('discipline-pages/*.html'))
    disc_items = [(get_title(f), f'discipline-pages/{f.stem}') for f in disc_pages]
    new_body.append(make_section('Categorias por Disciplina', disc_items, '', cols=2))

    # Produtos
    new_body.append(make_section('Produtos e Materiais Pedagogicos', produtos, '', cols=2))

    # Artigos (3 colunas porque sao 1350)
    new_body.append(make_section('Artigos e Dicas Pedagogicas', artigos,
                                  'artigos/', cols=3))

    # Cidades (4 colunas porque sao 794)
    cidade_links = [(name, f'{slug}/concurso-professor.html') for name, slug in cidades]
    new_body.append(make_section('Concursos da Educacao por Cidade',
                                  cidade_links, '', cols=4))

    body_html = '\n\n'.join(new_body)

    # Encontra container e substitui conteudo
    new_content = re.sub(
        r'(<div class="container">\s*)(.*?)(\s*</div>\s*<footer)',
        lambda m: m.group(1) + body_html + m.group(3),
        content,
        count=1,
        flags=re.DOTALL,
    )

    # Se o regex acima nao casar, tenta padrao alternativo
    if new_content == content:
        new_content = re.sub(
            r'(<div class="container">)(.*?)(</div>\s*<!-- ?footer)',
            lambda m: m.group(1) + '\n' + body_html + '\n' + m.group(3),
            content,
            count=1,
            flags=re.DOTALL,
        )

    if new_content == content:
        # Fallback: substitui tudo entre <div class="container"> e </body>
        new_content = re.sub(
            r'(<div class="container">)(.*?)(</div>\s*</body>)',
            lambda m: m.group(1) + '\n' + body_html + '\n' + m.group(3),
            content,
            count=1,
            flags=re.DOTALL,
        )

    # Atualiza title e description
    total = len(artigos) + len(produtos) + len(cidades) + len(disc_items)
    new_content = re.sub(
        r'<title>[^<]*</title>',
        f'<title>Mapa do Site - {total}+ paginas | Plano de Aula Pronto BNCC 2026</title>',
        new_content,
        count=1,
    )
    new_content = re.sub(
        r'(<meta name="description" content=")[^"]*(")',
        rf'\1Mapa completo: {len(produtos)} produtos, {len(artigos)} artigos, '
        rf'{len(cidades)} cidades, {len(disc_items)} categorias. BNCC 2026.\2',
        new_content,
        count=1,
    )

    if new_content == content:
        print('AVISO: nenhuma substituicao aplicada — checar padroes regex')
        return

    mapa.write_bytes(new_content.encode('utf-8'))
    print(f'Escrito {mapa}: {total}+ links no mapa do site')


if __name__ == '__main__':
    main()
