# CLAUDE.md

Documento de contexto operacional do site `planodeaulapronto.github.io`.

Ultima atualizacao local: 2026-05-16.

## Objetivo do site

O site `https://planodeaulapronto.github.io/` e um portal estatico no GitHub Pages para:

- Produtos pedagogicos prontos alinhados a BNCC.
- Artigos SEO sobre planos de aula, atividades, alfabetizacao, BNCC e pratica docente.
- Paginas programaticas de concursos da educacao por cidade e cargo.
- CTA principal para `https://www.aulagen.com.br/`, posicionado como plataforma de IA para professores e preparacao para concursos.

## Regras atuais de linkagem

- Artigos nao devem apontar para dominios externos antigos.
- Links externos permitidos nos CTAs: `https://www.aulagen.com.br/`.
- Produtos sao excecao: paginas em `/produto/*.html` e `/produtos/*.html` devem preservar os links de afiliado Hotmart corretos de cada produto.
- Nunca substituir `hotmartLink`, `Offer.url` ou `buy-btn-large` de produto por AulaGen.
- Links internos devem priorizar:
  - Home: `https://planodeaulapronto.github.io/`
  - Artigos: `/artigos/`
  - Produtos: `/produto/` e `/produtos/`
  - Cidades/concursos: `/cidades/` e `/{cidade}/{cargo}.html`
- Email oficial de contato: `planodeaulaprontobncc@gmail.com`.

## O que ja foi feito

### Artigos

- Processados 1.351 artigos em `/artigos/`.
- Adicionado SEO completo nos artigos:
  - `title`
  - `meta description`
  - `meta robots`
  - `canonical`
  - Open Graph
  - Twitter card
  - JSON-LD `Article`
  - JSON-LD `BreadcrumbList`
- Injetado CTA AulaGen no topo e no fim dos artigos.
- Injetado banner sticky AulaGen no topo de todos os artigos.
- Removidos links externos antigos dos artigos.
- Convertidas imagens externas antigas para caminhos locais quando possivel.
- Removidas mencoes e hotlinks antigos para `diariodaeducacao.com.br`.
- Padronizado o email de contato.

### Home

- Adicionado banner sticky AulaGen no topo.
- Adicionado CTA AulaGen na homepage.
- Adicionada listagem de artigos na homepage para reduzir orfandade dos artigos.
- Mantido link para artigos no menu lateral: `artigos/index.html`.
- Adicionados atalhos visiveis no topo da home para:
  - `artigos/index.html`
  - `#blog-artigos`
  - `cidades/index.html`
  - `https://www.aulagen.com.br/`
- Home deve funcionar como hub para produtos, artigos e concursos.

### Produtos

- Banner sticky AulaGen no topo de todas as paginas de produto.
- O banner AulaGen nao substitui nem altera a venda principal dos produtos.
- Restaurados os links Hotmart corretos dos 219 produtos no `products.json`.
- Restaurados os links Hotmart corretos em 438 paginas HTML de produto:
  - `/produto/*.html`
  - `/produtos/*.html`
- Restaurados `Offer.url` e `buy-btn-large` usando o historico Git exato de cada arquivo/produto.
- `Offer.url` do schema `Product` deve continuar apontando para Hotmart, nunca para AulaGen.
- Corrigido bug visual do SVG/WhatsApp gigante com CSS de seguranca:
  - `svg:not([width]):not([height]) { max-width:24px; max-height:24px; }`
- Mantida estrutura de paginas de produto com CTA principal para compra via Hotmart.

### Schema.org

- Otimizados schemas em 5.782 paginas principais.
- Cada pagina processada tem um unico bloco `SCHEMA-OPTIMIZED` com JSON-LD `@graph`.
- Home:
  - `EducationalOrganization`
  - `WebSite`
  - `CollectionPage`
  - `ItemList`
  - `BreadcrumbList`
- Artigos:
  - `BlogPosting`
  - `WebPage`
  - `FAQPage`
  - `BreadcrumbList`
- Produtos:
  - `Product`
  - `Offer`
  - `AggregateRating`
  - `Review`
  - `FAQPage`
  - `BreadcrumbList`
- Cidades/concursos:
  - `Article`
  - `WebPage`
  - `Service`
  - `City`
  - `FAQPage`
  - `BreadcrumbList`
- Nao criar `LocalBusiness` falso para cidades sem endereco fisico real. Para SEO local de cidade, usar `City`, `Place`, `Service` e `areaServed`.
- FAQPage deve ter perguntas visiveis na pagina via bloco `SCHEMA-FAQ-VISIBLE`.

### Responsividade

- Aplicado `responsive_hotfix.py` em 5.780 paginas.
- Ajustes mobile:
  - evita overflow horizontal;
  - limita SVGs gigantes;
  - ajusta grids de produtos;
  - ajusta banner AulaGen;
  - melhora leitura em celular;
  - ajusta cards, botoes, tabelas e menus.
- Testado com Chrome headless em telas mobile e desktop para home, artigo, produto e cidade.

### Concursos por cidade

- Criado gerador `build_cidades.py`.
- Base de municipios: `ibge_municipios.json`.
- Selecionadas 794 cidades prioritarias por quotas estaduais, capitais e grandes municipios.
- Geradas 3.970 paginas programaticas:
  - `/{cidade}/concurso-pedagogo.html`
  - `/{cidade}/concurso-professor.html`
  - `/{cidade}/pss-professor.html`
  - `/{cidade}/concurso-educacao-infantil.html`
  - `/{cidade}/concurso-auxiliar-educacao-infantil.html`
- Criado indice global:
  - `/cidades/index.html`
- Cada pagina de cidade/cargo inclui:
  - Head SEO
  - canonical
  - JSON-LD Article
  - JSON-LD BreadcrumbList
  - conteudo unico por cidade e cargo
  - CTA AulaGen para estudo com IA
  - links para outros cargos da mesma cidade
  - banner sticky AulaGen no topo

### Sitemap e robots

- `robots.txt` permite rastreamento e aponta para:
  - `https://planodeaulapronto.github.io/sitemap.xml`
- `build_cidades.py` foi ajustado para regenerar o sitemap de forma limpa, sem duplicar URLs a cada execucao.
- O sitemap atual deve conter URLs unicas para home, paginas estaticas, artigos, produtos, produtos antigos, discipline-pages e paginas de cidade/cargo.

### Scripts adicionados/alterados

- `fix_articles.py`
  - Corrige SEO e CTAs dos artigos.
- `fix_residue.py`
  - Remove residuos externos, regenera sitemap basico e verifica robots.
- `build_cidades.py`
  - Gera paginas programaticas de concursos por cidade.
- `inject_banner.py`
  - Script antigo de injecao parcial de banner e correcao de SVG.
- `sitewide_banner.py`
  - Injeta banner sticky AulaGen em todos os HTMLs do site.
  - Nao altera Hotmart, `buy-btn-large`, `Offer.url` ou links de compra.
- `responsive_hotfix.py`
  - Injeta CSS responsivo global nas paginas principais.
- `schema_optimization.py`
  - Remove JSON-LD antigo e injeta `@graph` schema.org otimizado por tipo de pagina.
  - Mantem `Product.offers.url` apontando para Hotmart.

## Fluxo recomendado de manutencao

Depois de editar produtos, artigos ou paginas programaticas:

```powershell
cd C:\Users\tonib\Desktop\planodeaulapronto-repo
$env:PYTHONIOENCODING='utf-8'
python build_cidades.py
python sitewide_banner.py
python responsive_hotfix.py
python schema_optimization.py
python sitewide_banner.py
```

Observacao: rode `sitewide_banner.py` novamente depois de `schema_optimization.py` sempre que quiser garantir o banner no topo de absolutamente todas as paginas.

Depois validar:

```powershell
git status --short
(Select-String -Path sitemap.xml -Pattern '<loc>' | Measure-Object).Count
Select-String -Path index.html -Pattern 'AULAGEN-STICKY-BANNER'
Select-String -Path artigos\aula-sobre-racismo-como-abordar-o-tema-na-educacao.html -Pattern 'AULAGEN-STICKY-BANNER'
Select-String -Path produto\plano-de-aula-fisica-ensino-medio.html -Pattern 'AULAGEN-STICKY-BANNER|go.hotmart.com|buy-btn-large|svg-bugfix|SCHEMA-OPTIMIZED'
Select-String -Path sao-paulo\concurso-professor.html -Pattern 'AULAGEN-STICKY-BANNER'
```

Validacao critica dos produtos:

```powershell
Select-String -Path products.json -Pattern 'go.hotmart.com' | Measure-Object
Select-String -Path produto\*.html,produtos\*.html -Pattern 'class="buy-btn-large"' | Measure-Object
Select-String -Path produto\*.html,produtos\*.html -Pattern 'href="https://go.hotmart.com' | Measure-Object
```

Validacao de schema:

```powershell
@'
from pathlib import Path
import re,json
rx=re.compile(r'<script[^>]+type=["\\']application/ld\\+json["\\'][^>]*>(.*?)</script>', re.I|re.S)
errors=[]
for p in Path('.').rglob('*.html'):
    s=p.read_text(encoding='utf-8',errors='ignore')
    if 'SCHEMA-OPTIMIZED start' not in s:
        continue
    scripts=rx.findall(s)
    if len(scripts)!=1:
        errors.append((str(p),len(scripts)))
        continue
    try:
        data=json.loads(scripts[0])
        assert data.get('@context')=='https://schema.org'
        assert '@graph' in data
    except Exception as e:
        errors.append((str(p),str(e)))
print('schema_errors=', len(errors))
print(errors[:10])
'@ | python -
```

## Deploy

Repositorio remoto:

```text
https://planodeaulapronto.github.io/
```

Branch de deploy:

```text
main
```

Importante:

- Nunca salvar token GitHub em arquivo.
- Nunca commitar token.
- Nunca escrever token em `CLAUDE.md`.
- Depois de qualquer push feito com token colado em chat, revogar o token no GitHub.

## Roadmap sugerido

### SEO tecnico

- Adicionar links mais visiveis na home para:
  - `/artigos/index.html`
  - `/cidades/index.html`
  - produtos mais importantes
- Criar pagina `/artigos/index.html` mais forte, com categorias e paginacao.
- Atualizar `mapa-do-site.html` para incluir artigos e concursos por cidade.
- Separar sitemap por tipo se o arquivo ficar pesado:
  - `sitemap-artigos.xml`
  - `sitemap-produtos.xml`
  - `sitemap-cidades.xml`
  - `sitemap-index.xml`
- Submeter `sitemap.xml` no Google Search Console apos deploy.

### Conteudo

- Revisar templates das paginas de cidade para reduzir repeticao.
- Incluir perguntas frequentes por cargo/cidade com JSON-LD `FAQPage`.
- Criar paginas por estado:
  - `/sp/concursos-educacao.html`
  - `/mg/concursos-educacao.html`
  - etc.
- Criar cluster de conteudo para:
  - LDB
  - ECA
  - BNCC
  - DCNEI
  - conhecimentos pedagogicos
  - simulados para professor

### Conversao AulaGen

- Testar diferentes CTAs:
  - "Gerar simulado agora"
  - "Criar plano de estudos"
  - "Preparar concurso com IA"
- Criar UTMs nos links para AulaGen se precisar medir origem:
  - `?utm_source=github_pages&utm_medium=seo&utm_campaign=concursos`
- Adicionar CTA especifico por tipo de pagina:
  - artigos: plano de aula e atividades
  - concursos: simulados, questoes comentadas e plano de estudos
  - produtos: IA para complementar materiais prontos

### Performance

- Validar peso da home depois da lista de artigos.
- Evitar imagens externas.
- Conferir lazy loading em produtos.
- Minificar CSS inline futuramente se o tamanho total ficar alto.

## Estado de indexacao esperado

Nao existe garantia absoluta de indexacao pelo Google. O que foi feito remove os principais bloqueadores:

- `robots.txt` permissivo.
- `meta robots` index/follow.
- `canonical` por pagina.
- sitemap com URLs.
- links internos para artigos e cidades.
- CTAs e links internos que reduzem paginas orfas.

Depois do deploy:

1. Abrir Google Search Console.
2. Reenviar `https://planodeaulapronto.github.io/sitemap.xml`.
3. Inspecionar algumas URLs de artigo e cidade.
4. Solicitar indexacao manual de amostras importantes.
5. Acompanhar "Descoberta - atualmente nao indexada" e "Rastreada - atualmente nao indexada".
