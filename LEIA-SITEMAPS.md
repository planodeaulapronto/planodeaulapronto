# 📌 Sitemaps — Plano de Aula Pronto

## Estrutura dos Sitemaps

O site utiliza **3 arquivos de sitemap** no padrão [Sitemap Protocol](https://www.sitemaps.org/protocol.html):

| Arquivo | Tipo | Conteúdo |
|---|---|---|
| `sitemap.xml` | **Sitemap Index** | Índice que aponta para os 2 sitemaps abaixo |
| `sitemap-produtos.xml` | Urlset | Página inicial + páginas de disciplinas + páginas de produtos |
| `sitemap-artigos.xml` | Urlset | Índice de artigos + todos os artigos individuais |

## Como Funciona no GitHub Pages

- **GitHub Pages serve arquivos `.xml` com o Content-Type `application/xml`** automaticamente.
- O arquivo `.nojekyll` na raiz impede o Jekyll de processar os arquivos (essencial).
- O `robots.txt` declara os 3 sitemaps para os crawlers.

### robots.txt
```
User-agent: *
Allow: /

Sitemap: https://planodeaulapronto.github.io/sitemap.xml
Sitemap: https://planodeaulapronto.github.io/sitemap-produtos.xml
Sitemap: https://planodeaulapronto.github.io/sitemap-artigos.xml
```

## Como Gerar / Atualizar os Sitemaps

```bash
node generate-sitemap.js
```

Esse script lê `products.json`, os HTMLs em `discipline-pages/` e `artigos/`, e gera os 3 XMLs.

**Após gerar, fazer commit e push:**
```bash
git add sitemap.xml sitemap-produtos.xml sitemap-artigos.xml
git commit -m "seo: atualiza sitemaps"
git push
```

## Problema: "Não foi possível buscar o sitemap" no Google Search Console

### Causas Possíveis

1. **Demora de propagação** — GitHub Pages leva alguns minutos para atualizar após o push. O Google pode tentar buscar antes da publicação.
2. **Cache do GitHub Pages** — Pode demorar até ~10 minutos para servir a versão nova.
3. **Encoding incorreto** — Os XMLs devem ser UTF-8 **sem BOM** (Byte Order Mark). O Node.js em Windows pode gerar com BOM.
4. **Line endings CRLF** — Windows usa `\r\n`, mas o padrão XML espera `\n`. Em geral funciona, mas pode causar problemas.
5. **Google Search Console instável** — Às vezes o GSC simplesmente falha temporariamente ao buscar sitemaps.

### Solução Aplicada

O script `generate-sitemap.js` foi ajustado para:
- Gerar XMLs com **line endings LF** (`\n`, não `\r\n`)
- Usar encoding UTF-8 **sem BOM**
- Atualizar `lastmod` para a data atual

### Como Verificar se os Sitemaps estão Online

Acesse diretamente no navegador:
- https://planodeaulapronto.github.io/sitemap.xml
- https://planodeaulapronto.github.io/sitemap-produtos.xml
- https://planodeaulapronto.github.io/sitemap-artigos.xml

Se abrir o XML normalmente, os arquivos estão OK. O problema é do Google Search Console.

### Como Reenviar no Google Search Console

1. Vá em [Google Search Console > Sitemaps](https://planodeaulapronto.github.io/)
2. **Delete** todos os sitemaps antigos (com e sem `?v=3`)
3. Adicione **apenas 1** sitemap: `sitemap.xml`  
   (O Google seguirá automaticamente os links internos para `sitemap-produtos.xml` e `sitemap-artigos.xml`)
4. Aguarde **24-48 horas** para o Google processar

> **IMPORTANTE**: Não envie 6 sitemaps diferentes. Envie apenas `sitemap.xml` (o índice).
> O Google encontrará os sub-sitemaps automaticamente a partir dele.

## Limites do Sitemap

| Regra | Limite |
|---|---|
| Tamanho máximo por arquivo | 50 MB (descomprimido) |
| URLs máximas por arquivo | 50.000 |
| Arquivos atuais | ~55 KB (produtos) e ~335 KB (artigos) ✅ |

## Histórico de Alterações

| Data | Ação |
|---|---|
| 2026-02-27 | Primeira versão dos sitemaps (index + produtos + artigos) |
| 2026-03-03 | Regeneração com encoding correto (UTF-8 sem BOM, LF) |
