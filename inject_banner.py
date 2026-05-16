"""
Patch:
1. Injeta banner sticky AulaGen no topo de TODOS os artigos, produtos e index
2. Corrige SVG sem width/height nos produtos (bug do whatsapp gigante)
3. Garante que a barra do topo eh sticky (position:sticky;top:0;z-index:9999)
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STICKY_BANNER = """<!-- AULAGEN-STICKY-BANNER start -->
<div id="aulagen-sticky-banner" style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 50%,#ec4899 100%);color:#fff;padding:12px 18px;position:sticky;top:0;z-index:9999;box-shadow:0 2px 14px rgba(0,0,0,.2);font-family:system-ui,sans-serif">
  <div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
    <div style="display:flex;align-items:center;gap:12px;flex:1;min-width:260px">
      <div style="background:rgba(255,255,255,.2);width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0">🤖</div>
      <div style="line-height:1.3">
        <div style="font-weight:800;font-size:.98rem">AulaGen — IA para Professores</div>
        <div style="font-size:.82rem;opacity:.92">50+ ferramentas IA: planos, provas, atividades adaptadas e simulados de concursos.</div>
      </div>
    </div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="background:#fff;color:#4F46E5;padding:9px 18px;border-radius:7px;font-weight:800;text-decoration:none;font-size:.86rem;white-space:nowrap;box-shadow:0 4px 10px rgba(0,0,0,.15);flex-shrink:0">Conhecer &rarr;</a>
  </div>
</div>
<!-- AULAGEN-STICKY-BANNER end -->
"""

SVG_FIX_CSS = '<style id="svg-bugfix">svg:not([width]):not([height]){max-width:24px !important;max-height:24px !important;} #aulagen-sticky-banner svg{max-width:none !important;max-height:none !important;}</style>\n</head>'

def patch_file(path: Path, kind: str) -> bool:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if raw.startswith("﻿"):
        raw = raw.lstrip("﻿")
    changed = False
    # 1. Remove banner antigo se existir (idempotente)
    raw_new = re.sub(r"<!-- AULAGEN-STICKY-BANNER start.*?<!-- AULAGEN-STICKY-BANNER end -->\s*", "", raw, flags=re.DOTALL)
    raw_new = re.sub(r"<!-- TOP-AULAGEN-BANNER start.*?<!-- TOP-AULAGEN-BANNER end -->\s*", "", raw_new, flags=re.DOTALL)
    # Tambem remove banner antigo aulagen-banner inline na home
    raw_new = re.sub(r'<div id="aulagen-banner"[\s\S]*?</div>\s*</div>\s*</div>\s*', "", raw_new)
    # 2. Injeta banner sticky logo apos <body>
    if "<body" in raw_new:
        raw_new = re.sub(r"(<body[^>]*>)", r"\1\n" + STICKY_BANNER, raw_new, count=1)
        changed = True
    # 3. Aplica fix de SVG nos produtos (bug whatsapp/lupa gigante)
    if kind == "produto":
        # corrige svgs do whatsapp sem dimensoes - adiciona width/height inline
        raw_new = re.sub(
            r'<svg(\s+xmlns="[^"]*")?\s+viewBox="0 0 448 512"',
            r'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 448 512"',
            raw_new,
        )
        # injeta CSS de seguranca antes do </head>
        if "id=\"svg-bugfix\"" not in raw_new:
            raw_new = raw_new.replace("</head>", SVG_FIX_CSS, 1)
            changed = True
    if raw_new != raw:
        path.write_text(raw_new, encoding="utf-8", newline="\n")
        return True
    return changed

def main() -> None:
    targets: list[tuple[Path, str]] = []
    for sub in ("artigos", "produto", "produtos"):
        d = ROOT / sub
        if d.is_dir():
            kind = "produto" if sub in ("produto", "produtos") else "artigo"
            for f in d.glob("*.html"):
                targets.append((f, kind))

    # paginas programaticas de cidades/concurso
    for d in ROOT.iterdir():
        if d.is_dir() and (d / "concurso-professor.html").exists():
            for f in d.glob("*.html"):
                targets.append((f, "cidade"))

    cidades_index = ROOT / "cidades" / "index.html"
    if cidades_index.exists():
        targets.append((cidades_index, "cidade"))

    # tambem index.html e mapa
    for name in ("index.html", "mapa-do-site.html"):
        p = ROOT / name
        if p.exists():
            targets.append((p, "home"))

    print(f"Processando {len(targets)} arquivos...")
    n_ok = 0
    for i, (path, kind) in enumerate(targets, 1):
        try:
            if patch_file(path, kind):
                n_ok += 1
            if i % 300 == 0:
                print(f"  ...{i}/{len(targets)}")
        except Exception as e:
            print(f"  ! erro em {path.name}: {e}")
    print(f"\nOK {n_ok}/{len(targets)} arquivos modificados.")

if __name__ == "__main__":
    main()
