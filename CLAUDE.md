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
- Removidas mencoes de `planodeaulapronto.github.io`.
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

- Injetado banner sticky AulaGen em `/produto/*.html` e `/produtos/*.html`.
- Corrigido bug visual do SVG/WhatsApp gigante com CSS de seguranca:
  - `svg:not([width]):not([height]) { max-width:24px; max-height:24px; }`
- Mantida estrutura de paginas de produto com CTA principal.

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
  - Injeta banner sticky AulaGen em artigos, produtos, home, mapa e paginas de cidade/concurso.

## Fluxo recomendado de manutencao

Depois de editar produtos, artigos ou paginas programaticas:

```powershell
cd C:\Users\tonib\Desktop\planodeaulapronto-repo
$env:PYTHONIOENCODING='utf-8'
python build_cidades.py
python inject_banner.py
```

Depois validar:

```powershell
git status --short
(Select-String -Path sitemap.xml -Pattern '<loc>' | Measure-Object).Count
Select-String -Path index.html -Pattern 'AULAGEN-STICKY-BANNER'
Select-String -Path artigos\aula-sobre-racismo-como-abordar-o-tema-na-educacao.html -Pattern 'AULAGEN-STICKY-BANNER'
Select-String -Path produto\plano-de-aula-fisica-ensino-medio.html -Pattern 'svg-bugfix|AULAGEN-STICKY-BANNER'
Select-String -Path sao-paulo\concurso-professor.html -Pattern 'AULAGEN-STICKY-BANNER'
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
