# 📄 Documentação Completa: Projeto Plano de Aula Pronto BNCC 2026

Este documento detalha toda a infraestrutura, estratégia de SEO e processos técnicos implementados no site [https://planodeaulapronto.github.io/](https://planodeaulapronto.github.io/).

---

## 🚀 1. Visão Geral do Projeto
O objetivo do site é dominar o nicho de materiais pedagógicos no Brasil para o ano de 2026, focando no termo-chave principal: **"Plano de Aula Pronto BNCC 2026"**. 

O projeto funciona como uma "máquina de SEO", atraindo professores através de uma vasta biblioteca de artigos informativos e convertendo-os em compradores através de páginas de produtos detalhadas que levam ao Checkout da Hotmart.

---

## 🏗️ 2. Arquitetura Técnica
O site é uma aplicação estática (Jamstack) gerada via scripts Node.js, garantindo velocidade máxima de carregamento (essencial para SEO mobile).

### Estrutura de Pastas:
- `/artigos/`: Contém os 1.351 guias pedagógicos premium.
- `/produtos/`: Contém as 219 páginas individuais de produtos (kits e pacotes).
- `/images/`: Repositório de capas e mockups dos materiais.
- `index.html`: Landing page principal otimizada.
- `sitemap.xml`: Mapa completo com as 1.589 URLs para indexação no Google.

---

## 📈 3. Estratégia de SEO de Elite (V3.0)
A implementação seguiu os mais altos padrões do Google para 2026:

### A. Dados Estruturados (Schema.org JSON-LD):
- **Product & Merchant Center**: Inclui preço, moeda (BRL), disponibilidade, avaliações reais e políticas de frete/devolução. Isso faz com que as estrelas e o preço apareçam diretamente na busca do Google.
- **FAQPage**: Expande a presença visual na busca, respondendo dúvidas comuns e aumentando o CTR (taxa de clique).
- **BlogPosting**: Identifica os artigos como conteúdo educacional de alta autoridade.
- **BreadcrumbList**: Facilita a navegação do robô do Google pela hierarquia do site.

### B. Linkagem "Dofollow":
- 100% dos links (internos e externos) utilizam `rel="dofollow"`.
- Isso garante que a autoridade (link equity) flua livremente entre a Home, os Artigos e o domínio principal (Plano de Aula Pronto), fortalecendo todo o ecossistema.

### C. Conteúdo Anti-Thin Content:
- **Artigos**: Média de 600-1000 palavras de conteúdo pedagógico puro + 600 palavras de estrutura. Totalizando ~1.200 a 1.500 termos por página.
- **Riqueza Semântica**: Inclusão sistemática de códigos BNCC reais (ex: EI03MA01) e termos técnicos do MEC.

---

## 🛠️ 4. Fluxo de Geração (Scripts Node.js)
O site é mantido através de quatro scripts principais localizados na raiz:

1.  **`generate-landing.js`**: Gera a Home Page com o catálogo dinâmico de produtos.
2.  **`generate-product-pages.js`**: Cria as páginas de venda individuais com Schema de Merchant Center.
3.  **`generate-articles.js`**: Processa os 1.351 resultados da OpenAI Batch API e cria os guias educativos.
4.  **`generate-sitemap.js`**: Compila todas as páginas criadas em um arquivo XML para o Google Search Console.

---

## 💰 5. Sistema de Afiliados (Hotmart)
- **Rastreamento Único**: Todos os links de compra utilizam o parâmetro `?src=github`.
- **Origem**: Isso permite identificar exatamente quais vendas vieram desta infraestrutura de SEO no painel da Hotmart.

---

## 🌐 6. Deploy e Hospedagem
- **Hospedagem**: GitHub Pages.
- **Domínio**: `https://planodeaulapronto.github.io/`
- **Repositório**: `planodeaulapronto/planodeaulapronto`

---

## 📅 7. Calendário de Atualizações
- **Lote 1 (Concluído)**: Estrutura base e primeiros artigos.
- **Lote 2 (Concluído)**: Expansão massiva (+1000 artigos) e implementação do SEO de Elite 2026.
- **Próximos Passos**: Monitoramento via Google Search Console e acompanhamento de indexação.

---
*Documentação gerada automaticamente em 23/02/2026.*
