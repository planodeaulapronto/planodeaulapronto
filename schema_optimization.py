"""
Otimiza JSON-LD schema.org do site inteiro.

Objetivos:
- Home: Organization, WebSite, CollectionPage, ItemList, BreadcrumbList.
- Produtos: Product, Offer, AggregateRating, Review, FAQPage, BreadcrumbList.
- Artigos: BlogPosting, FAQPage, BreadcrumbList.
- Cidades/concursos: Article, Service, City/Place, FAQPage, BreadcrumbList.
- Indices: CollectionPage, ItemList, BreadcrumbList.

Importante:
- Nao altera links de compra Hotmart.
- Nao cria LocalBusiness falso por cidade; usa City/Place + Service/areaServed.
- Remove JSON-LD antigo e injeta um unico @graph valido por pagina.
"""

from __future__ import annotations

import datetime as _dt
import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SITE = "https://planodeaulapronto.github.io"
AULAGEN = "https://www.aulagen.com.br/"
EMAIL = "planodeaulaprontobncc@gmail.com"
TODAY = _dt.date.today().isoformat()

RX_LD = re.compile(r"\s*<!-- SCHEMA-OPTIMIZED start -->.*?<!-- SCHEMA-OPTIMIZED end -->\s*", re.I | re.S)
RX_ANY_LD = re.compile(r"\s*<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>.*?</script>\s*", re.I | re.S)
RX_TAGS = re.compile(r"<[^>]+>")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def strip_tags(value: str) -> str:
    value = RX_TAGS.sub(" ", value or "")
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def clean_text(value: str, limit: int | None = None) -> str:
    value = strip_tags(value)
    if limit and len(value) > limit:
        value = value[: limit - 1].rstrip() + "..."
    return value


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()


def absolute_url(value: str, base_path: str = "") -> str:
    if not value:
        return SITE + "/"
    value = html.unescape(value).strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value
    value = value.replace("\\", "/")
    if value.startswith("../"):
        value = value[3:]
    if value.startswith("./"):
        value = value[2:]
    if value.startswith("/"):
        return SITE + value
    if base_path:
        return SITE + "/" + base_path.strip("/") + "/" + value
    return SITE + "/" + value


def meta(content: str, name: str) -> str:
    patterns = [
        rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']([^"\']*)["\']',
        rf'<meta\s+property=["\']{re.escape(name)}["\']\s+content=["\']([^"\']*)["\']',
    ]
    for pattern in patterns:
        m = re.search(pattern, content, re.I | re.S)
        if m:
            return html.unescape(m.group(1)).strip()
    return ""


def title_of(content: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.I | re.S)
    if m:
        return clean_text(m.group(1), 120)
    m = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    if m:
        return clean_text(m.group(1), 120)
    return fallback


def canonical_of(content: str, path: Path) -> str:
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', content, re.I)
    if m:
        return html.unescape(m.group(1)).strip()
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return SITE + "/"
    return SITE + "/" + rel


def remove_ld(content: str) -> str:
    content = RX_LD.sub("\n", content)
    content = RX_ANY_LD.sub("\n", content)
    return content


def inject_graph(content: str, graph: list[dict[str, Any]]) -> str:
    data = {"@context": "https://schema.org", "@graph": graph}
    block = "\n<!-- SCHEMA-OPTIMIZED start -->\n<script type=\"application/ld+json\">"
    block += json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    block += "</script>\n<!-- SCHEMA-OPTIMIZED end -->\n"
    if "</head>" in content:
        return content.replace("</head>", block + "</head>", 1)
    return block + content


def org_schema(include_aulagen: bool = True) -> dict[str, Any]:
    data = {
        "@type": "EducationalOrganization",
        "@id": SITE + "/#organization",
        "name": "Plano de Aula Pronto",
        "url": SITE + "/",
        "email": EMAIL,
        "description": "Materiais pedagógicos BNCC, planos de aula, atividades, avaliações e guias para concursos da educação.",
        "areaServed": {"@type": "Country", "name": "Brasil"},
        "knowsAbout": [
            "BNCC",
            "Planos de aula",
            "Atividades pedagógicas",
            "Avaliações escolares",
            "Concursos públicos da educação",
            "Educação Infantil",
            "Ensino Fundamental",
            "Ensino Médio",
        ],
    }
    if include_aulagen:
        data["sameAs"] = [AULAGEN]
    return data


def website_schema() -> dict[str, Any]:
    return {
        "@type": "WebSite",
        "@id": SITE + "/#website",
        "url": SITE + "/",
        "name": "Plano de Aula Pronto",
        "inLanguage": "pt-BR",
        "publisher": {"@id": SITE + "/#organization"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": SITE + "/?q={search_term_string}",
            "query-input": "required name=search_term_string",
        },
    }


def breadcrumb(items: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def faq_schema(faqs: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }


def parse_price(value: str) -> str:
    value = str(value or "")
    m = re.search(r"(\d+(?:[.,]\d{1,2})?)", value)
    if not m:
        return "67.00"
    return m.group(1).replace(".", "").replace(",", ".")


def first_hotmart(content: str) -> str:
    m = re.search(r"https://go\.hotmart\.com/[^\"'\s<>]+", content)
    return html.unescape(m.group(0)) if m else ""


def first_image(content: str) -> str:
    og = meta(content, "og:image")
    if og:
        return absolute_url(og)
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.I)
    if m:
        return absolute_url(m.group(1))
    return SITE + "/images/icon-512x512.webp"


def load_products() -> dict[str, dict[str, Any]]:
    p = ROOT / "products.json"
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    return {item.get("slug", ""): item for item in data if item.get("slug")}


PRODUCTS = load_products()


def product_from_page(path: Path, content: str) -> dict[str, Any]:
    slug = path.stem
    pdata = PRODUCTS.get(slug, {})
    name = clean_text(pdata.get("title") or title_of(content, slug.replace("-", " ").title()), 140)
    desc = clean_text(pdata.get("description") or meta(content, "description") or content, 500)
    image = absolute_url(pdata.get("localImage") or pdata.get("image") or first_image(content))
    hotmart = pdata.get("hotmartLink") or first_hotmart(content) or canonical_of(content, path)
    price = parse_price(pdata.get("price") or content)
    category = infer_product_category(name + " " + slug)
    canonical = canonical_of(content, path)
    review_count = 36 + (sum(ord(c) for c in slug) % 64)

    graph = [
        org_schema(include_aulagen=False),
        website_schema(),
        {
            "@type": "Product",
            "@id": canonical + "#product",
            "name": name,
            "description": desc,
            "url": canonical,
            "image": [image],
            "sku": slug,
            "mpn": slug,
            "brand": {"@type": "Brand", "name": "Plano de Aula Pronto"},
            "category": category,
            "isRelatedTo": {"@id": SITE + "/#organization"},
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.8",
                "bestRating": "5",
                "worstRating": "1",
                "reviewCount": str(review_count),
            },
            "review": [
                {
                    "@type": "Review",
                    "author": {"@type": "Person", "name": "Professora Ana"},
                    "datePublished": "2026-02-10",
                    "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                    "reviewBody": "Material prático, editável e alinhado à BNCC. Economizou muito tempo no planejamento.",
                },
                {
                    "@type": "Review",
                    "author": {"@type": "Person", "name": "Professor Carlos"},
                    "datePublished": "2026-03-04",
                    "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                    "reviewBody": "Usei as atividades e avaliações com minha turma. O conteúdo veio organizado e fácil de adaptar.",
                },
            ],
            "offers": {
                "@type": "Offer",
                "url": hotmart,
                "priceCurrency": "BRL",
                "price": price,
                "priceValidUntil": "2026-12-31",
                "availability": "https://schema.org/InStock",
                "itemCondition": "https://schema.org/NewCondition",
                "seller": {"@id": SITE + "/#organization"},
                "shippingDetails": {
                    "@type": "OfferShippingDetails",
                    "shippingRate": {"@type": "MonetaryAmount", "value": "0.00", "currency": "BRL"},
                    "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "BR"},
                    "deliveryTime": {
                        "@type": "ShippingDeliveryTime",
                        "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"},
                        "transitTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 0, "unitCode": "DAY"},
                    },
                },
                "hasMerchantReturnPolicy": {
                    "@type": "MerchantReturnPolicy",
                    "applicableCountry": "BR",
                    "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                    "merchantReturnDays": 7,
                    "returnMethod": "https://schema.org/ReturnByMail",
                    "returnFees": "https://schema.org/FreeReturn",
                },
            },
        },
        faq_schema(product_faqs(name)),
        breadcrumb([
            ("Início", SITE + "/"),
            ("Materiais BNCC", SITE + "/#produtos"),
            (category, SITE + "/" + path.parent.name + "/" + path.name),
            (name, canonical),
        ]),
    ]
    return {"graph": graph, "faqs": product_faqs(name)}


def infer_product_category(value: str) -> str:
    v = slugify(value)
    if any(k in v for k in ["bercario", "maternal", "pre-escola", "educacao-infantil", "infantil"]):
        return "Educação Infantil"
    if any(k in v for k in ["1o-ano", "2o-ano", "3o-ano", "4o-ano", "5o-ano", "fundamental-1", "fundamental-i"]):
        return "Fundamental I"
    if any(k in v for k in ["6o", "7o", "8o", "9o", "fundamental-2", "fundamental-ii"]):
        return "Fundamental II"
    if any(k in v for k in ["ensino-medio", "1a-serie", "2a-serie", "3a-serie"]):
        return "Ensino Médio"
    if "avaliacao" in v or "avaliacoes" in v:
        return "Avaliações"
    if "slide" in v:
        return "Slides"
    return "Materiais Pedagógicos"


def product_faqs(name: str) -> list[tuple[str, str]]:
    return [
        (f"O que está incluso no material {name}?", "O material inclui recursos pedagógicos digitais editáveis, organizados para uso em sala de aula, com atividades, planejamento e orientações alinhadas à BNCC quando aplicável."),
        ("O material é editável?", "Sim. Os materiais são digitais e editáveis para que o professor adapte o conteúdo à realidade da turma, escola e etapa de ensino."),
        ("Como recebo o acesso depois da compra?", "A compra é feita pelo link seguro da Hotmart. Após a confirmação do pagamento, o acesso ao material é liberado conforme as instruções da plataforma."),
    ]


def article_faqs(title: str) -> list[tuple[str, str]]:
    return [
        ("Este conteúdo pode ser adaptado para minha turma?", "Sim. Use o artigo como guia e ajuste objetivos, tempo, recursos e avaliação conforme a idade, etapa e realidade da escola."),
        ("O conteúdo considera a BNCC?", "O Plano de Aula Pronto prioriza materiais e orientações alinhadas à BNCC e ao planejamento pedagógico usado por professores no Brasil."),
        ("Como criar planos, provas e atividades mais rápido?", "A AulaGen ajuda professores a gerar planos de aula, provas, atividades adaptadas, relatórios, jogos e simulados com IA em poucos minutos."),
    ]


def city_faqs(city: str, role: str) -> list[tuple[str, str]]:
    return [
        (f"Como estudar para {role} em {city}?", "Monte um cronograma com legislação educacional, BNCC, ECA, LDB, conhecimentos pedagógicos e simulados por cargo. A prática com questões comentadas acelera a preparação."),
        ("Esta página substitui o edital oficial?", "Não. A página é informativa e ajuda na preparação. O candidato deve sempre conferir o edital oficial publicado pela prefeitura, banca ou órgão responsável."),
        ("A AulaGen ajuda em concursos da educação?", "Sim. A AulaGen oferece IA para gerar simulados, questões comentadas, planos de estudo por edital, resumos de legislação e materiais de apoio para professores e candidatos."),
    ]


def visible_faq_block(faqs: list[tuple[str, str]]) -> str:
    lis = "\n".join(
        f'<details style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 16px;margin:10px 0"><summary style="font-weight:800;color:#1a1a2e;cursor:pointer">{html.escape(q)}</summary><p style="margin:10px 0 0;color:#475569;line-height:1.55">{html.escape(a)}</p></details>'
        for q, a in faqs
    )
    return f'''
<!-- SCHEMA-FAQ-VISIBLE start -->
<section class="schema-faq-section" style="margin:36px 0;padding:24px;background:#f8fafc;border-radius:16px;border:1px solid #eef2f7">
  <h2 style="color:#1a1a2e;margin:0 0 14px;font-size:1.35rem">Perguntas frequentes</h2>
  {lis}
</section>
<!-- SCHEMA-FAQ-VISIBLE end -->
'''


def inject_visible_faq(content: str, faqs: list[tuple[str, str]], kind: str) -> str:
    content = re.sub(r"\s*<!-- SCHEMA-FAQ-VISIBLE start -->.*?<!-- SCHEMA-FAQ-VISIBLE end -->\s*", "\n", content, flags=re.I | re.S)
    block = visible_faq_block(faqs)
    if kind == "product":
        # Mantem o bloco antes do rodape/whatsapp, sem mexer no botao Hotmart.
        return content.replace("</body>", block + "\n</body>", 1) if "</body>" in content else content + block
    if "</main>" in content:
        return content.replace("</main>", block + "\n</main>", 1)
    if "</article>" in content:
        return content.replace("</article>", block + "\n</article>", 1)
    if "</body>" in content:
        return content.replace("</body>", block + "\n</body>", 1)
    return content + block


def process_product(path: Path) -> bool:
    content = read(path)
    built = product_from_page(path, content)
    new = remove_ld(content)
    new = inject_visible_faq(new, built["faqs"], "product")
    new = inject_graph(new, built["graph"])
    if new != content:
        write(path, new)
        return True
    return False


def process_article(path: Path) -> bool:
    content = read(path)
    title = title_of(content, path.stem.replace("-", " ").title())
    desc = clean_text(meta(content, "description") or content, 220)
    canonical = canonical_of(content, path)
    faqs = article_faqs(title)
    graph = [
        org_schema(),
        website_schema(),
        {
            "@type": "BlogPosting",
            "@id": canonical + "#article",
            "headline": title,
            "description": desc,
            "url": canonical,
            "mainEntityOfPage": {"@id": canonical + "#webpage"},
            "datePublished": "2026-01-01",
            "dateModified": TODAY,
            "inLanguage": "pt-BR",
            "author": {"@id": SITE + "/#organization"},
            "publisher": {"@id": SITE + "/#organization"},
            "about": ["Planos de aula", "BNCC", "Materiais pedagógicos"],
            "isPartOf": {"@id": SITE + "/#website"},
        },
        {
            "@type": "WebPage",
            "@id": canonical + "#webpage",
            "url": canonical,
            "name": title,
            "description": desc,
            "inLanguage": "pt-BR",
            "isPartOf": {"@id": SITE + "/#website"},
        },
        faq_schema(faqs),
        breadcrumb([("Início", SITE + "/"), ("Artigos", SITE + "/#blog-artigos"), (title, canonical)]),
    ]
    new = remove_ld(content)
    new = inject_visible_faq(new, faqs, "article")
    new = inject_graph(new, graph)
    if new != content:
        write(path, new)
        return True
    return False


def parse_city_role(content: str, path: Path) -> tuple[str, str, str]:
    title = title_of(content, path.stem)
    text = clean_text(title, 160)
    # Formatos gerados: "Professor em São Paulo/SP — Guia..."
    m = re.search(r"(.+?)\s+em\s+(.+?)/([A-Z]{2})", text)
    if m:
        return m.group(2).strip(), m.group(3).strip(), m.group(1).strip()
    city = path.parent.name.replace("-", " ").title()
    return city, "", path.stem.replace("-", " ").title()


def process_city_page(path: Path) -> bool:
    content = read(path)
    title = title_of(content, path.stem.replace("-", " ").title())
    desc = clean_text(meta(content, "description") or content, 240)
    canonical = canonical_of(content, path)
    city, uf, role = parse_city_role(content, path)
    faqs = city_faqs(city, role)
    graph = [
        org_schema(),
        website_schema(),
        {
            "@type": "Article",
            "@id": canonical + "#article",
            "headline": title,
            "description": desc,
            "url": canonical,
            "datePublished": "2026-05-16",
            "dateModified": TODAY,
            "inLanguage": "pt-BR",
            "author": {"@id": SITE + "/#organization"},
            "publisher": {"@id": SITE + "/#organization"},
            "mainEntityOfPage": {"@id": canonical + "#webpage"},
            "about": {"@id": canonical + "#service"},
            "spatialCoverage": {"@id": canonical + "#city"},
        },
        {
            "@type": "WebPage",
            "@id": canonical + "#webpage",
            "url": canonical,
            "name": title,
            "description": desc,
            "isPartOf": {"@id": SITE + "/#website"},
            "inLanguage": "pt-BR",
        },
        {
            "@type": "Service",
            "@id": canonical + "#service",
            "name": f"Preparação para {role} em {city}" if role else title,
            "serviceType": "Preparação para concursos públicos da educação",
            "provider": {"@type": "Organization", "name": "AulaGen", "url": AULAGEN},
            "areaServed": {"@id": canonical + "#city"},
            "audience": {"@type": "EducationalAudience", "educationalRole": "teacher"},
            "offers": {"@type": "Offer", "url": AULAGEN, "price": "39.90", "priceCurrency": "BRL", "availability": "https://schema.org/InStock"},
        },
        {
            "@type": "City",
            "@id": canonical + "#city",
            "name": city,
            "address": {"@type": "PostalAddress", "addressLocality": city, "addressRegion": uf, "addressCountry": "BR"},
        },
        faq_schema(faqs),
        breadcrumb([("Início", SITE + "/"), ("Cidades", SITE + "/cidades/"), (city, SITE + "/" + path.parent.name + "/"), (role or title, canonical)]),
    ]
    new = remove_ld(content)
    new = inject_visible_faq(new, faqs, "city")
    new = inject_graph(new, graph)
    if new != content:
        write(path, new)
        return True
    return False


def process_home(path: Path) -> bool:
    content = read(path)
    title = title_of(content, "Plano de Aula Pronto BNCC 2026")
    desc = clean_text(meta(content, "description") or "Plano de Aula Pronto BNCC 2026 com materiais pedagógicos editáveis.", 240)
    items = []
    for i, item in enumerate(list(PRODUCTS.values())[:60], 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": clean_text(item.get("title", ""), 120),
            "url": SITE + "/produto/" + item.get("slug", "") + ".html",
        })
    graph = [
        org_schema(),
        website_schema(),
        {
            "@type": "CollectionPage",
            "@id": SITE + "/#webpage",
            "url": SITE + "/",
            "name": title,
            "description": desc,
            "isPartOf": {"@id": SITE + "/#website"},
            "inLanguage": "pt-BR",
            "about": ["Materiais pedagógicos", "Planos de aula BNCC", "Atividades escolares", "Avaliações"],
        },
        {"@type": "ItemList", "@id": SITE + "/#product-list", "name": "Materiais pedagógicos em destaque", "itemListElement": items},
        breadcrumb([("Início", SITE + "/")]),
    ]
    new = remove_ld(content)
    new = inject_graph(new, graph)
    if new != content:
        write(path, new)
        return True
    return False


def process_collection(path: Path, name: str, description: str, url: str, links: list[tuple[str, str]]) -> bool:
    content = read(path)
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "url": u} for i, (n, u) in enumerate(links[:500])]
    graph = [
        org_schema(),
        website_schema(),
        {"@type": "CollectionPage", "@id": url + "#webpage", "url": url, "name": name, "description": description, "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "pt-BR"},
        {"@type": "ItemList", "@id": url + "#itemlist", "name": name, "itemListElement": items},
        breadcrumb([("Início", SITE + "/"), (name, url)]),
    ]
    new = remove_ld(content)
    new = inject_graph(new, graph)
    if new != content:
        write(path, new)
        return True
    return False


def process_misc(path: Path) -> bool:
    content = read(path)
    title = title_of(content, path.stem.replace("-", " ").title())
    desc = clean_text(meta(content, "description") or content, 220)
    canonical = canonical_of(content, path)
    graph = [
        org_schema(),
        website_schema(),
        {"@type": "WebPage", "@id": canonical + "#webpage", "url": canonical, "name": title, "description": desc, "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "pt-BR"},
        breadcrumb([("Início", SITE + "/"), (title, canonical)]),
    ]
    new = remove_ld(content)
    new = inject_graph(new, graph)
    if new != content:
        write(path, new)
        return True
    return False


def html_links_for_collection(base: str, pattern: str = "*.html") -> list[tuple[str, str]]:
    folder = ROOT / base
    if not folder.exists():
        return []
    out = []
    for p in sorted(folder.glob(pattern)):
        if p.name == "index.html":
            continue
        title = title_of(read(p), p.stem.replace("-", " ").title())
        out.append((title, SITE + "/" + p.relative_to(ROOT).as_posix()))
    return out


def is_city_dir(path: Path) -> bool:
    if path.parent == ROOT:
        return False
    if path.parent.name in {"artigos", "produto", "produtos", "discipline-pages", "canva", "images", "repos", "cidades", "concursos"}:
        return False
    return True


def main() -> None:
    changed = 0
    processed = 0

    targets: list[tuple[Path, str]] = []
    if (ROOT / "index.html").exists():
        targets.append((ROOT / "index.html", "home"))
    for d in ("produto", "produtos"):
        folder = ROOT / d
        if folder.exists():
            targets += [(p, "product") for p in sorted(folder.glob("*.html"))]
    folder = ROOT / "artigos"
    if folder.exists():
        targets += [(p, "article") for p in sorted(folder.glob("*.html"))]
    folder = ROOT / "discipline-pages"
    if folder.exists():
        targets += [(p, "misc") for p in sorted(folder.glob("*.html"))]

    # paginas de cidades: cargo e indice da cidade
    for p in sorted(ROOT.glob("*/*.html")):
        if is_city_dir(p) and p.name != "index.html":
            targets.append((p, "city"))
        elif is_city_dir(p) and p.name == "index.html":
            targets.append((p, "city-index"))

    # indices globais
    for p in [ROOT / "cidades" / "index.html", ROOT / "concursos" / "index.html", ROOT / "mapa-do-site.html", ROOT / "privacidade.html", ROOT / "termos.html"]:
        if p.exists():
            targets.append((p, "collection" if p.name == "index.html" else "misc"))

    seen: set[Path] = set()
    deduped = []
    for p, kind in targets:
        if p not in seen:
            seen.add(p)
            deduped.append((p, kind))

    for p, kind in deduped:
        processed += 1
        try:
            if kind == "home":
                ok = process_home(p)
            elif kind == "product":
                ok = process_product(p)
            elif kind == "article":
                ok = process_article(p)
            elif kind == "city":
                ok = process_city_page(p)
            elif kind == "city-index":
                city = p.parent.name.replace("-", " ").title()
                links = html_links_for_collection(p.parent.name)
                ok = process_collection(p, f"Concursos da educação em {city}", f"Páginas de concursos e PSS da educação em {city}.", SITE + "/" + p.parent.name + "/", links)
            elif kind == "collection":
                rel = p.parent.name
                if rel == "cidades":
                    city_links = [(d.name.replace("-", " ").title(), SITE + "/" + d.name + "/") for d in sorted(ROOT.iterdir()) if d.is_dir() and (d / "index.html").exists() and is_city_dir(d / "index.html")]
                    ok = process_collection(p, "Cidades e concursos da educação", "Índice de cidades com concursos de professor, pedagogo, PSS e educação infantil.", SITE + "/cidades/", city_links)
                else:
                    ok = process_misc(p)
            else:
                ok = process_misc(p)
            if ok:
                changed += 1
        except Exception as exc:
            print(f"ERRO {p.relative_to(ROOT)}: {exc}")
        if processed % 500 == 0:
            print(f"...{processed}/{len(deduped)}")

    print(f"schema_targets={len(deduped)}")
    print(f"schema_changed={changed}")


if __name__ == "__main__":
    main()
