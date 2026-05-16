"""
Limpa residuos de dominios externos antigos em arquivos publicos e de suporte.

O script:
1. Converte imagens externas antigas para caminhos locais em /images.
2. Troca mencoes do dominio antigo pelo dominio GitHub Pages atual.
3. Troca mencoes textuais da marca antiga por "Plano de Aula Pronto".
4. Mantem o sitemap atual intacto. O sitemap limpo e gerado por build_cidades.py.

Uso:
  python fix_residue.py
"""

from __future__ import annotations

import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://planodeaulapronto.github.io"

RX_IMAGE_URL = re.compile(
    r"https?://diariodaeducacao\.com\.br/(?:images/)?([^\"'\s<>]+?\.(?:webp|png|jpg|jpeg|gif))",
    re.IGNORECASE,
)
RX_DOMAIN_TEXT = re.compile(r"diariodaeducacao\.com\.br", re.IGNORECASE)
RX_BRAND_TEXT = re.compile(r"Di[aá]rio\s+da\s+Educa[cç][aã]o", re.IGNORECASE)


def image_prefix(path: Path) -> str:
    rel = os.path.relpath(ROOT / "images", path.parent).replace("\\", "/")
    return rel


def patch_file(path: Path) -> tuple[int, int, int]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if raw.startswith("\ufeff"):
        raw = raw.lstrip("\ufeff")

    def image_replace(match: re.Match) -> str:
        filename = match.group(1).split("/")[-1]
        return f"{image_prefix(path)}/{filename}"

    new_raw, n_img = RX_IMAGE_URL.subn(image_replace, raw)
    new_raw, n_url = RX_DOMAIN_TEXT.subn("planodeaulapronto.github.io", new_raw)
    new_raw, n_brand = RX_BRAND_TEXT.subn("Plano de Aula Pronto", new_raw)

    if new_raw != raw:
        path.write_text(new_raw, encoding="utf-8", newline="\n")
    return n_img, n_url, n_brand


def main() -> None:
    targets: list[Path] = []
    for ext in ("*.html", "*.json", "*.md"):
        targets.extend(
            p for p in ROOT.rglob(ext)
            if ".git" not in p.parts
        )

    print(f"Patcheando {len(targets)} arquivos...")
    total_img = total_url = total_brand = 0
    for i, path in enumerate(targets, 1):
        try:
            n_img, n_url, n_brand = patch_file(path)
            total_img += n_img
            total_url += n_url
            total_brand += n_brand
        except Exception as exc:
            print(f"  ! erro em {path}: {exc}")
        if i % 500 == 0:
            print(f"  ...{i}/{len(targets)}")

    robots = ROOT / "robots.txt"
    robots.write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"OK imagens externas convertidas: {total_img}")
    print(f"OK mencoes de URL substituidas: {total_url}")
    print(f"OK mencoes de marca substituidas: {total_brand}")
    print("OK robots.txt verificado")


if __name__ == "__main__":
    main()
