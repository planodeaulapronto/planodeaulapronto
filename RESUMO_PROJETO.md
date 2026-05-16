# Resumo do Projeto: Reestruturação de URLs e Layout

Este documento resume as solicitações do usuário e o progresso atual para continuidade do trabalho.

## Objetivos Solicitados
1.  **Reestruturação de URLs**: Mudar URLs de `produtos/` para `produto/` e padronizar o slug para `plano-de-aula-[disciplina]-[nivel]`.
2.  **Remoção de Datas e Termos**: Remover termos como "atividades", "2025", "2026" e datas das URLs.
3.  **Layout de Grid**:
    *   **Desktop**: 6 colunas por linha.
    *   **Mobile**: 2 colunas por linha.
4.  **Limpeza de HTML**: Garantir que tags HTML (ex: `<h2>`, `<p>`) não apareçam como texto bruto nos cards de produtos.
5.  **Implantação**: Gerar todos os arquivos (219 produtos) e enviar para o GitHub.

---

## O Que Já Foi Feito ✅
1.  **Padronização de Dados (`products.json`)**:
    *   Títulos limpos de tags HTML.
    *   Slugs reescritos seguindo o padrão solicitado.
    *   Script de transformação criado: `transform-products.js`.
2.  **Scripts Geradores Atualizados**:
    *   `generate-landing.js`, `generate-product-pages.js`, `generate-discipline-pages.js`, `generate-sitemap.js`, `generate-articles.js`.
    *   Caminho de saída alterado para a pasta `produto/`.
    *   Links internos atualizados para apontar para `produto/`.
3.  **Layout Atualizado**:
    *   `generate-landing.js` configurado para 6 colunas (desktop) e 2 colunas (mobile).

---

## Próximos Passos (Pendentes) 🛠️
1.  **Correção de Tags HTML nos Cards**:
    *   Os scripts `generate-landing.js` e `generate-discipline-pages.js` ainda estão escapando tags HTML nas descrições, fazendo com que apareçam como texto. Necessário usar Regex para remover tags antes de exibir o resumo.
2.  **Consistência de Grid**:
    *   Verificar e aplicar o layout de 6 colunas em `generate-discipline-pages.js`.
3.  **Geração e Verificação**:
    *   Rodar todos os scripts geradores.
    *   Confirmar que a pasta `produto/` contém os 219 arquivos.
4.  **Deploy**:
    *   Commit e push de todas as alterações para o repositório GitHub.

---

## Detalhes Técnicos
*   **Node.js**: Localizado em `C:\Users\plantao\Documents\buch\agilzap\servidor\node-local\node.exe`.
*   **Base URL**: `https://planodeaulapronto.github.io/
*   **Dados**: `products.json` é a fonte da verdade.
