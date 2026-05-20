# -*- coding: utf-8 -*-
"""
Corrige problemas de qualidade que prejudicam indexacao:
1. Remove prefixos literais "H2:"/"H3:" antes de cada heading
2. Desfaz <p><h2>...</h2></p> invalidos (block dentro de inline)
3. Corrige mojibake (UTF-8 duplo encoding) com ftfy
4. Substitui alt="${p.title.replace(...)}" pelo titulo do h4 adjacente
5. Normaliza marca no rodape (Diario da Educacao -> Plano de Aula Pronto)

Uso:
    python fix_seo_quality.py          # dry-run, mostra contagens
    python fix_seo_quality.py --apply  # aplica as mudancas
    python fix_seo_quality.py --apply --file artigos/aula-sobre-racismo-como-abordar-o-tema-na-educacao.html
"""
import re
import sys
import argparse
from pathlib import Path

import ftfy

ROOT = Path('.')

RE_H_PREFIX = re.compile(r'<h([1-6])>H[1-6]:\s*')
RE_P_WRAP_H = re.compile(r'<p>\s*(<h[1-6][^>]*>.*?</h[1-6]>)\s*</p>', re.DOTALL)
# <p><h?>...</h?> orfao (sem </p> de fechamento) - remove o <p> aberto antes do heading
RE_P_OPEN_H = re.compile(r'<p>\s*(<h[1-6][^>]*>)')

# Markdown leak standalone: <p>#### H3: Texto</p> ou <p>#### <strong>Texto</strong></p>
# Permite tags inline (<strong>, <em>, etc.) mas NAO <br> nem novo <p — fica no padrao single-line
RE_P_HASH = re.compile(r'<p>(#{1,6})\s+(?:H[1-6]:\s*)?((?:[^<]|<(?!br|/p|p\b))+?)</p>')

# Markdown leak inline: <p>#### H3: Titulo<br>resto</p> ou <p>#### <strong>Titulo</strong><br>
# Vira: <h?>Titulo</h?><p>resto</p> (preservando tags inline)
RE_P_HASH_OPEN = re.compile(r'<p>(#{2,6})\s+(?:H[1-6]:\s*)?((?:[^<]|<(?!br|/p|p\b))+?)<br\s*/?>')

# Markdown leak inline no meio: ...<br>#### H3: Titulo<br>...
# Vira <strong> (mais seguro do que mexer em estrutura de p/h)
RE_INLINE_HASH = re.compile(r'(<br\s*/?>)(#{2,6})\s+(?:H[1-6]:\s*)?([^<\n]+?)(?=<br|</p>)')

BROKEN_ALT_LITERAL = "${p.title.replace(/\"/g, '&quot;')}"

# Rodape: "Diario da Educacao - Materiais Pedagogicos BNCC 2026"
RE_FOOTER_BRAND = re.compile(
    r'(<a[^>]*href="https://planodeaulapronto\.github\.io/"[^>]*>)\s*'
    r'Di[aá]rio da Educa[cç][aã]o[^<]*</a>',
    re.IGNORECASE
)

def fix_broken_alts(content):
    """Substitui ${p.title.replace(...)} pelo texto do <h4> mais proximo a frente."""
    parts = []
    last = 0
    n_with_title = 0
    n_empty = 0
    while True:
        i = content.find(BROKEN_ALT_LITERAL, last)
        if i == -1:
            parts.append(content[last:])
            break
        parts.append(content[last:i])
        h4_open = content.find('<h4', i)
        h4_close = content.find('</h4>', h4_open) if h4_open != -1 else -1
        if h4_open != -1 and h4_close != -1 and (h4_open - i) < 600:
            ge = content.find('>', h4_open) + 1
            title = content[ge:h4_close].strip()
            parts.append(title.replace('"', '&quot;'))
            n_with_title += 1
        else:
            n_empty += 1
        last = i + len(BROKEN_ALT_LITERAL)
    return ''.join(parts), n_with_title, n_empty

def hash_to_h(m):
    n_hashes = len(m.group(1))
    text = m.group(2).strip()
    level = max(2, min(6, n_hashes))
    return f'<h{level}>{text}</h{level}>'


def p_hash_open_to_h(m):
    """<p>#### H3: Titulo<br>  =>  <h?>Titulo</h?><p>"""
    n_hashes = len(m.group(1))
    text = m.group(2).strip()
    level = max(3, min(6, n_hashes))
    return f'<h{level}>{text}</h{level}><p>'


def inline_hash_to_h(m):
    """<br>#### H3: Titulo  =>  <br><strong>Titulo</strong>"""
    sep = m.group(1)
    text = m.group(3).strip()
    return f'{sep}<strong>{text}</strong>'


def fix_html(content):
    changes = dict.fromkeys(
        ['h_prefix', 'p_wrap_h', 'broken_alt', 'broken_alt_fb', 'mojibake', 'footer', 'md_hash'],
        0
    )

    new, n = RE_H_PREFIX.subn(r'<h\1>', content)
    changes['h_prefix'] = n
    content = new

    new, n = RE_P_HASH.subn(hash_to_h, content)
    changes['md_hash'] += n
    content = new

    new, n = RE_P_HASH_OPEN.subn(p_hash_open_to_h, content)
    changes['md_hash'] += n
    content = new

    new, n = RE_INLINE_HASH.subn(inline_hash_to_h, content)
    changes['md_hash'] += n
    content = new

    new, n = RE_P_WRAP_H.subn(r'\1', content)
    changes['p_wrap_h'] = n
    content = new

    new, n = RE_P_OPEN_H.subn(r'\1', content)
    changes['p_wrap_h'] += n
    content = new

    content, n_title, n_empty = fix_broken_alts(content)
    changes['broken_alt'] = n_title
    changes['broken_alt_fb'] = n_empty

    fixed = ftfy.fix_text(content)
    if fixed != content:
        changes['mojibake'] = 1
        content = fixed

    new, n = RE_FOOTER_BRAND.subn(
        r'\1Plano de Aula Pronto - Materiais Pedagógicos BNCC 2026</a>',
        content,
    )
    changes['footer'] = n
    content = new

    return content, changes


def collect_files(only_file=None):
    if only_file:
        return [Path(only_file)]
    files = []
    files.append(Path('index.html'))
    files.extend(sorted(Path('artigos').glob('*.html')))
    files.extend(sorted(Path('produto').glob('*.html')))
    files.extend(sorted(Path('produtos').glob('*.html')))
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        if d.name in ('artigos', 'produto', 'produtos', 'images', 'memory', '__pycache__', 'cidades'):
            continue
        for f in d.glob('*.html'):
            files.append(f)
    files.extend(sorted(Path('cidades').glob('*.html')))
    return [f for f in files if f.exists()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--file')
    args = ap.parse_args()

    files = collect_files(args.file)
    total = dict.fromkeys(
        ['files', 'changed', 'h_prefix', 'p_wrap_h', 'broken_alt', 'broken_alt_fb', 'mojibake', 'footer', 'md_hash'],
        0
    )

    for f in files:
        try:
            raw = f.read_bytes()
            original = raw.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f'ERRO lendo {f}: {e}', file=sys.stderr)
            continue
        new, changes = fix_html(original)
        total['files'] += 1
        for k in ('h_prefix', 'p_wrap_h', 'broken_alt', 'broken_alt_fb', 'mojibake', 'footer', 'md_hash'):
            total[k] += changes[k]
        if new != original:
            total['changed'] += 1
            if args.apply:
                # Preserva line endings originais (LF/CRLF) gravando em binario
                f.write_bytes(new.encode('utf-8'))

    print('=== Resumo ===')
    print(f'Arquivos analisados: {total["files"]}')
    print(f'Arquivos {"alterados" if args.apply else "que mudariam"}: {total["changed"]}')
    print(f'Prefixos H2:/H3: removidos: {total["h_prefix"]}')
    print(f'Leaks markdown #### convertidos: {total["md_hash"]}')
    print(f'<p><h?></h?></p> desfeitos: {total["p_wrap_h"]}')
    print(f'Alts ${{...}} resolvidos com titulo: {total["broken_alt"]}')
    print(f'Alts ${{...}} caidos para alt vazio (fallback): {total["broken_alt_fb"]}')
    print(f'Arquivos com mojibake corrigido: {total["mojibake"]}')
    print(f'Rodapes "Diario da Educacao" normalizados: {total["footer"]}')


if __name__ == '__main__':
    main()
