"""
Garante banner AulaGen no topo de todas as paginas HTML.

Nao altera CTA, botao de compra, Hotmart, schema Product ou links internos.
Remove banners antigos duplicados e injeta um unico banner sticky logo apos <body>.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BANNER = """<!-- AULAGEN-STICKY-BANNER start -->
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
<!-- AULAGEN-STICKY-BANNER end -->
"""


def patch(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8-sig", errors="ignore")
    before = raw
    raw = re.sub(r"\s*<!-- AULAGEN-STICKY-BANNER start -->.*?<!-- AULAGEN-STICKY-BANNER end -->\s*", "\n", raw, flags=re.I | re.S)
    raw = re.sub(r"\s*<!-- TOP-AULAGEN-BANNER start -->.*?<!-- TOP-AULAGEN-BANNER end -->\s*", "\n", raw, flags=re.I | re.S)
    if "<body" in raw:
        raw = re.sub(r"(<body[^>]*>)", r"\1\n" + BANNER, raw, count=1, flags=re.I)
    else:
        raw = BANNER + raw
    if raw != before:
        path.write_text(raw, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    files = sorted(ROOT.rglob("*.html"))
    changed = 0
    for i, path in enumerate(files, 1):
        if patch(path):
            changed += 1
        if i % 1000 == 0:
            print(f"...{i}/{len(files)}")
    print(f"banner_targets={len(files)}")
    print(f"banner_changed={changed}")


if __name__ == "__main__":
    main()
