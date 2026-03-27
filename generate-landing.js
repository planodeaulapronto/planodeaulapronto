const fs = require('fs');
const path = require('path');

const products = JSON.parse(fs.readFileSync(path.join(__dirname, 'products.json'), 'utf8'));
console.log(`Loaded ${products.length} products`);

const BASE_URL = 'https://planodeaulapronto.github.io';
const buildTime = new Date().toLocaleString('pt-BR');

// Categorize products
function categorize(slug) {
  const s = slug.toLowerCase();
  if (s.includes('bercario') || s.includes('maternal') || s.includes('pre-escola') || s.includes('educacao-infantil') || s.includes('cartas-de-intencao') || s.includes('planner-educacao-especial') || s.includes('50-projetos-para-pre') || s.includes('ebooks-educacao-infantil') || s.includes('planejamentos-educacao-infantil')) return 'Educação Infantil';
  if (s.includes('1o-ao-5o') || s.includes('1-ao-5') || s.includes('anos-iniciais') || s.includes('1o-ano') || s.includes('2o-ano') || s.includes('3o-ano') || s.includes('4o-ano') || s.includes('5o-ano') || s.includes('1-ano') || s.includes('2-ano') || s.includes('3-ano') || s.includes('4-ano') || s.includes('5-ano')) return 'Ensino Fundamental I';
  if (s.includes('6o-ao-9o') || s.includes('6-ao-9') || s.includes('fundamental-2')) return 'Ensino Fundamental II';
  if (s.includes('ensino-medio') || s.includes('novo-ensino-medio')) return 'Ensino Médio';
  if (s.includes('eja') || s.includes('educacao-jovens-adultos')) return 'EJA';
  if (s.includes('educacao-especial') || s.includes('tdah') || s.includes('autismo') || s.includes('dislexia') || s.includes('libras') || s.includes('estimulacao-cognitiva') || s.includes('aee') || s.includes('sindrome-down')) return 'Educação Especial';
  if (s.includes('alfabetizacao') || s.includes('consciencia-fonologica') || s.includes('alfabetinho')) return 'Alfabetização';
  if (s.includes('jogos-pedagogicos') || s.includes('datas-comemorativas') || s.includes('biblicas') || s.includes('producao-interpretacao') || s.includes('ingles-espanhol') || s.includes('kit-matematica')) return 'Materiais Complementares';
  return 'Materiais Pedagógicos';
}

const categories = {};
const catOrder = [
  'Educação Infantil',
  'Ensino Fundamental I',
  'Ensino Fundamental II',
  'Ensino Médio',
  'Alfabetização',
  'EJA',
  'Educação Especial',
  'Materiais Complementares',
  'Materiais Pedagógicos'
];

const catColors = {
  'Educação Infantil': { bg: '#FF6B9D', dark: '#E91E63', light: '#FCE4EC', gradient: 'linear-gradient(135deg, #FF6B9D, #E91E63)' },
  'Ensino Fundamental I': { bg: '#4FC3F7', dark: '#0288D1', light: '#E1F5FE', gradient: 'linear-gradient(135deg, #4FC3F7, #0288D1)' },
  'Ensino Fundamental II': { bg: '#66BB6A', dark: '#2E7D32', light: '#E8F5E9', gradient: 'linear-gradient(135deg, #66BB6A, #2E7D32)' },
  'Ensino Médio': { bg: '#AB47BC', dark: '#7B1FA2', light: '#F3E5F5', gradient: 'linear-gradient(135deg, #AB47BC, #7B1FA2)' },
  'Alfabetização': { bg: '#FF7043', dark: '#D84315', light: '#FBE9E7', gradient: 'linear-gradient(135deg, #FF7043, #D84315)' },
  'EJA': { bg: '#26A69A', dark: '#00695C', light: '#E0F2F1', gradient: 'linear-gradient(135deg, #26A69A, #00695C)' },
  'Educação Especial': { bg: '#5C6BC0', dark: '#283593', light: '#E8EAF6', gradient: 'linear-gradient(135deg, #5C6BC0, #283593)' },
  'Materiais Complementares': { bg: '#FFA726', dark: '#E65100', light: '#FFF3E0', gradient: 'linear-gradient(135deg, #FFA726, #E65100)' },
  'Materiais Pedagógicos': { bg: '#78909C', dark: '#37474F', light: '#ECEFF1', gradient: 'linear-gradient(135deg, #78909C, #37474F)' }
};

const catIcons = {
  'Educação Infantil': '🧒',
  'Ensino Fundamental I': '📚',
  'Ensino Fundamental II': '📖',
  'Ensino Médio': '🎓',
  'Alfabetização': '🔤',
  'EJA': '👨‍🎓',
  'Educação Especial': '💙',
  'Materiais Complementares': '🎯',
  'Materiais Pedagógicos': '📋'
};

products.forEach(p => {
  const cat = categorize(p.slug);
  if (!categories[cat]) categories[cat] = [];
  categories[cat].push(p);
});

// Generate category nav buttons
const navCategories = ['Educação Infantil', 'Ensino Fundamental I', 'Ensino Fundamental II', 'Ensino Médio'];
const navLabels = { 'Ensino Fundamental I': 'Fundamental I', 'Ensino Fundamental II': 'Fundamental II' };

function generateCatNav() {
  return navCategories.filter(c => categories[c] && categories[c].length > 0).map(cat => {
    const colors = catColors[cat];
    const icon = catIcons[cat];
    const label = navLabels[cat] || cat;
    const id = cat.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-').toLowerCase();
    return `<a href="#${id}" rel="dofollow" class="cat-btn" style="background: ${colors.gradient}">
              <span class="cat-icon">${icon}</span>
              <span class="cat-name">${label}</span>
              <span class="cat-count">${categories[cat].length}</span>
            </a>`;
  }).join('\n            ');
}

// Helper to strip HTML for Node.js
const stripHtml = (html) => (html || '')
  .replace(/<[^>]*>?/gm, ' ')
  .replace(/\s+/g, ' ')
  .trim();

// Generate product cards for a category
function generateCards(prods) {
  return prods.map(p => {
    const title = stripHtml(p.title).replace(/"/g, '&quot;');
    const desc = stripHtml(p.description).substring(0, 80).replace(/"/g, '&quot;');
    const imgSrc = p.localImage || `images/${p.slug}.webp`;

    let buyLink = p.hotmartLink || p.link || '';
    if (buyLink.includes('go.hotmart.com')) {
      const urlBase = buyLink.split('?')[0];
      buyLink = `${urlBase}?src=github`;
    } else {
      buyLink = buyLink.includes('?') ? `${buyLink}&src=github` : `${buyLink}?src=github`;
    }
    const price = p.price ? `R$ ${p.price}` : '';
    const discount = p.discount ? `-${p.discount}%` : '';

    const imgFallback = `this.onerror=null; if(this.src.includes('produtos-alfabetinho')){ this.src=this.src.replace('produtos-alfabetinho','produtos-bncc').replace('-1024x1024',''); } else { this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22300%22><rect fill=%22%23f0f0f0%22 width=%22300%22 height=%22300%22/><text x=%22150%22 y=%22150%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2216%22>Sem Imagem</text></svg>'; }`;

    return `
              <div class="product-card">
                <div class="card-image">
                  <img src="${imgSrc}" alt="${title}" loading="lazy" onerror="${imgFallback}">
                  ${discount ? `<span class="discount-badge">${discount}</span>` : ''}
                </div>
                <div class="card-body">
                  <a href="produto/${p.slug}.html" rel="dofollow" style="text-decoration: none; color: inherit;">
                    <h3 class="card-title">${title}</h3>
                  </a>
                  <p class="card-desc">${desc}${desc.length >= 80 ? '...' : ''}</p>
                  <div class="card-footer">
                    ${price ? `<span class="card-price">${price}</span>` : ''}
                    <a href="${buyLink}" target="_blank" rel="nofollow" class="buy-btn">Acessar</a>
                  </div>
                </div>
              </div>`;
  }).join('');
}

// Generate category sections
function generateSections() {
  return catOrder.filter(c => categories[c] && categories[c].length > 0).map(cat => {
    const colors = catColors[cat];
    const icon = catIcons[cat];
    const id = cat.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-').toLowerCase();
    return `
        <section class="category-section" id="${id}">
          <div class="category-header" style="background: ${colors.gradient}">
            <h2>${icon} ${cat}</h2>
            <span class="section-count">${categories[cat].length} produtos</span>
          </div>
          <div class="products-grid">
            ${generateCards(categories[cat])}
          </div>
        </section>`;
  }).join('\n');
}

// Construct the HTML using string concatenation to avoid syntax errors with nested backticks
let html = '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n' +
  '  <meta charset="UTF-8">\n' +
  '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n' +
  '  <title>Plano de Aula Pronto BNCC 2026 - Baixar em Word e PDF Editável</title>\n' +
  '  <meta name="description" content="Plano de Aula Pronto BNCC 2026. Baixe plano de aula diário, semanal, bimestral e anual, editável em Word e PDF para imprimir. Materiais completos de acordo com a BNCC para todos os anos.">\n' +
  '  <meta name="robots" content="index, follow">\n' +
  '  <link rel="canonical" href="https://planodeaulapronto.github.io/">\n' +
  '  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Outfit:wght@700;800&display=swap" rel="stylesheet">\n' +
  '  <style>\n' +
  '    :root {\n' +
  '      --primary: #6C63FF; --primary-dark: #5A52E0; --secondary: #FF6B9D; --accent: #00D4AA;\n' +
  '      --dark: #1a1a2e; --darker: #0f0f23; --card-bg: #ffffff; --text: #2d3748; --text-light: #718096;\n' +
  '      --radius: 16px; --shadow: 0 4px 20px rgba(0,0,0,0.08); --shadow-hover: 0 12px 40px rgba(0,0,0,0.15);\n' +
  '    }\n' +
  '    * { margin: 0; padding: 0; box-sizing: border-box; }\n' +
  '    body { font-family: \'Inter\', sans-serif; color: var(--text); background: #f8fafc; line-height: 1.6; overflow-x: hidden; }\n' +
  '    .hero { background: linear-gradient(135deg, var(--darker) 0%, #16213e 50%, #1a1a2e 100%); padding: 50px 20px 40px; text-align: center; position: relative; }\n' +
  '    .hero h1 { font-family: \'Outfit\', sans-serif; font-size: clamp(1.6rem, 4vw, 2.8rem); font-weight: 800; color: white; margin-bottom: 14px; }\n' +
  '    .hero h1 span { background: linear-gradient(135deg, #6C63FF, #FF6B9D, #00D4AA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }\n' +
  '    .hero p { color: rgba(255,255,255,0.7); font-size: 0.95rem; max-width: 600px; margin: 0 auto 24px; }\n' +
  '    .hero-stats { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; }\n' +
  '    .stat-number { font-family: \'Outfit\', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--accent); }\n' +
  '    .stat-label { color: rgba(255,255,255,0.6); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }\n' +
  '    .cat-nav { background: white; padding: 8px 12px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-bottom: 1px solid #edf2f7; }\n' +
  '    .cat-nav-inner { max-width: 1400px; margin: 0 auto; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }\n' +
  '    @media (max-width: 768px) {\n' +
  '      .cat-nav { padding: 6px 8px; }\n' +
  '      .cat-nav-inner { flex-wrap: nowrap; justify-content: flex-start; overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; gap: 6px; }\n' +
  '      .cat-nav-inner::-webkit-scrollbar { display: none; }\n' +
  '      .cat-nav .cat-btn { white-space: nowrap; padding: 6px 12px; font-size: 0.7rem; flex-shrink: 0; }\n' +
  '      .cat-nav .cat-icon { font-size: 0.85rem; }\n' +
  '      .cat-nav .cat-count { font-size: 0.6rem; }\n' +
  '    }\n' +
  '    .cat-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 50px; color: white; text-decoration: none; font-size: 0.8rem; font-weight: 700; transition: all 0.3s; }\n' +
  '    .cat-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.15); }\n' +
  '    .cat-icon { font-size: 1rem; }\n' +
  '    .cat-count { background: rgba(255,255,255,0.25); padding: 1px 6px; border-radius: 10px; font-size: 0.7rem; }\n' +
  '    .category-section { max-width: 1400px; margin: 24px auto; padding: 0 16px; }\n' +
  '    .category-header { padding: 14px 20px; border-radius: 12px 12px 0 0; display: flex; align-items: center; justify-content: space-between; }\n' +
  '    .category-header h2 { font-family: \'Outfit\', sans-serif; font-size: 1.1rem; color: white; }\n' +
  '    .section-count { color: rgba(255,255,255,0.8); font-size: 0.75rem; font-weight: 600; }\n' +
  '    .products-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 12px; background: #f1f5f9; border-radius: 0 0 var(--radius) var(--radius); }\n' +
  '    @media (min-width: 640px) { .products-grid { grid-template-columns: repeat(3, 1fr); } }\n' +
  '    @media (min-width: 900px) { .products-grid { grid-template-columns: repeat(4, 1fr); } }\n' +
  '    @media (min-width: 1100px) { .products-grid { grid-template-columns: repeat(5, 1fr); } }\n' +
  '    @media (min-width: 1360px) { .products-grid { grid-template-columns: repeat(6, 1fr); } }\n' +
  '    .product-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: all 0.3s; display: flex; flex-direction: column; height: 100%; }\n' +
  '    .product-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.12); transform: translateY(-2px); }\n' +
  '    .card-image { position: relative; width: 100%; aspect-ratio: 1/1; overflow: hidden; background: #f8fafc; }\n' +
  '    .card-image img { width: 100%; height: 100%; object-fit: cover; }\n' +
  '    .discount-badge { position: absolute; top: 6px; right: 6px; background: #ef4444; color: white; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 6px; }\n' +
  '    .card-body { padding: 8px 10px 10px; flex: 1; display: flex; flex-direction: column; }\n' +
  '    .card-title { font-family: \'Outfit\', sans-serif; font-size: 0.75rem; font-weight: 700; color: var(--dark); margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.25; min-height: 1.9em; }\n' +
  '    .card-desc { display: none; }\n' +
  '    .card-footer { margin-top: auto; display: flex; align-items: center; justify-content: space-between; gap: 6px; padding-top: 6px; border-top: 1px solid #f1f5f9; }\n' +
  '    .card-price { font-weight: 800; color: #16a34a; font-size: 0.8rem; white-space: nowrap; }\n' +
  '    .buy-btn { background: var(--primary); color: white; padding: 6px 10px; border-radius: 8px; text-decoration: none; font-size: 0.65rem; font-weight: 700; text-align: center; white-space: nowrap; transition: background 0.2s; }\n' +
  '    .buy-btn:hover { background: var(--primary-dark); }\n' +
  '    .search-container { max-width: 500px; margin: 20px auto 0; position: relative; z-index: 1001; }\n' +
  '    .search-box { position: relative; }\n' +
  '    .search-box input { width: 100%; padding: 12px 16px 12px 40px; border-radius: 50px; border: 2px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white; font-size: 0.9rem; outline: none; transition: all 0.3s; }\n' +
  '    .search-box input:focus { background: white; color: var(--dark); border-color: var(--primary); }\n' +
  '    #searchOverlay { position: absolute; top: calc(100% + 10px); left: 0; right: 0; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); z-index: 2000; max-height: 500px; overflow-y: auto; display: none; padding: 10px; border: 1px solid #eee; }\n' +
  '    .search-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); z-index: 1000; display: none; }\n' +
  '    .footer { background: var(--darker); color: white; padding: 24px 16px; text-align: center; margin-top: 40px; font-size: 0.8rem; }\n' +
  '    .whatsapp-float { position: fixed; bottom: 25px; right: 25px; background-color: #25d366; color: #fff; border-radius: 50px; padding: 12px 20px; display: flex; align-items: center; gap: 10px; text-decoration: none; font-family: inherit; font-weight: 700; font-size: 0.95rem; box-shadow: 0 4px 15px rgba(37,211,102,0.4); z-index: 9999; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }\n' +
  '    .whatsapp-float:hover { transform: scale(1.08) translateY(-5px); color: white; }\n' +
  '    .whatsapp-float svg { width: 24px; height: 24px; fill: currentColor; }\n' +
  '  </style>\n</head>\n<body>\n' +
  '  <div class="search-backdrop" id="searchBackdrop"></div>\n' +
  '  <header class="hero">\n    <div class="hero-content">\n' +
  '      <h1>Plano de Aula Pronto <span>BNCC 2026</span></h1>\n' +
  '      <p>Baixe <a href="https://planodeaulapronto.shop/" rel="dofollow" style="color: inherit; text-decoration: none; border-bottom: 1px dashed rgba(255,255,255,0.4);">plano de aula pronto</a> diário, semanal, bimestral e anual, editável em Word e PDF. Materiais 100% de acordo com a BNCC.</p>\n' +
  '      <div class="hero-stats">\n' +
  '        <a href="https://diariodaeducacao.com.br/" rel="dofollow" class="stat" style="text-decoration: none;"><div class="stat-number">' + products.length + '</div><div class="stat-label">Materiais</div></a>\n' +
  '        <div class="stat"><div class="stat-number">EDITÁVEL</div><div class="stat-label">Word/PDF</div></div>\n' +
  '        <a href="https://planodeaulapronto.shop/" rel="dofollow" class="stat" style="text-decoration: none;"><div class="stat-number">BNCC</div><div class="stat-label">Alinhados</div></a>\n' +
  '      </div>\n' +
  '      <div class="search-container">\n' +
  '        <div class="search-box">\n' +
  '          <input type="text" id="searchInput" placeholder="O que você está procurando? (ex: berçário, 1º ano...)" autocomplete="off">\n' +
  '          <div id="searchOverlay"></div>\n' +
  '        </div>\n' +
  '      </div>\n' +
  '    </div>\n  </header>\n' +
  '  <nav class="cat-nav">\n    <div class="cat-nav-inner">' + generateCatNav() + '</div>\n  </nav>\n' +
  '  <main id="productsMain">' + generateSections() + '</main>\n' +
  '  <section class="faq-section" style="max-width: 900px; margin: 60px auto; padding: 0 20px;">\n' +
  '    <h2 style="font-family: \'Outfit\', sans-serif; font-size: 2rem; text-align: center; margin-bottom: 40px; color: var(--dark);">Perguntas Frequentes 💡</h2>\n' +
  '    <div class="faq-grid" style="display: grid; gap: 20px;">\n' +
  '      <div class="faq-item" style="background: white; padding: 25px; border-radius: 16px; box-shadow: var(--shadow);">\n' +
  '        <h3 style="font-size: 1.1rem; margin-bottom: 10px; color: var(--primary);">O que é o <a href="https://planodeaulapronto.shop/" rel="dofollow" style="color: inherit; text-decoration: none; border-bottom: 1px dashed var(--primary);">Plano de Aula Pronto</a>?</h3>\n' +
  '        <p style="font-size: 0.95rem; color: var(--text-light);">É um material pedagógico completo e editável, desenvolvido para facilitar a rotina do professor, economizando tempo no planejamento e garantindo qualidade pedagógica.</p>\n' +
  '      </div>\n' +
  '      <div class="faq-item" style="background: white; padding: 25px; border-radius: 16px; box-shadow: var(--shadow);">\n' +
  '        <h3 style="font-size: 1.1rem; margin-bottom: 10px; color: var(--primary);">Os materiais são alinhados à BNCC?</h3>\n' +
  '        <p style="font-size: 0.95rem; color: var(--text-light);">Sim! Todos os nossos <a href="https://diariodaeducacao.com.br/" rel="dofollow" style="color: inherit; text-decoration: none; border-bottom: 1px dashed var(--primary);">planos de aula</a> estão 100% de acordo com a BNCC 2026, com códigos de habilidades e competências reais.</p>\n' +
  '      </div>\n' +
  '      <div class="faq-item" style="background: white; padding: 25px; border-radius: 16px; box-shadow: var(--shadow);">\n' +
  '        <h3 style="font-size: 1.1rem; margin-bottom: 10px; color: var(--primary);">O material é editável?</h3>\n' +
  '        <p style="font-size: 0.95rem; color: var(--text-light);">Sim, todos os arquivos são enviados em Word e PowerPoint, permitindo que você adapte o conteúdo conforme a necessidade da sua turma.</p>\n' +
  '      </div>\n' +
  '      <div class="faq-item" style="background: white; padding: 25px; border-radius: 16px; box-shadow: var(--shadow);">\n' +
  '        <h3 style="font-size: 1.1rem; margin-bottom: 10px; color: var(--primary);">Como recebo o acesso?</h3>\n' +
  '        <p style="font-size: 0.95rem; color: var(--text-light);">Após a confirmação do pagamento, você recebe os links para download imediatamente em seu e-mail.</p>\n' +
  '      </div>\n' +
  '    </div>\n' +
  '  </section>\n' +
  '  <footer class="footer">\n' +
  '    <p>© 2026 — <a href="https://diariodaeducacao.com.br/" rel="dofollow" style="color: white; text-decoration: none;">Materiais Pedagógicos BNCC</a> - Atualizado: ' + buildTime + '</p>\n' +
  '    <p style="margin-top: 10px; opacity: 0.8;">\n' +
  '      <a href="privacidade.html" style="color: white; margin: 0 10px;">Política de Privacidade</a> |\n' +
  '      <a href="termos.html" style="color: white; margin: 0 10px;">Termos de Uso</a> |\n' +
  '      <a href="https://planodeaulapronto.shop/" rel="dofollow" style="color: white; margin: 0 10px;">Plano de Aula Pronto</a>\n' +
  '    </p>\n' +
  '  </footer>\n' +
  '  <a href="https://wa.me/5541987746386?text=' + encodeURIComponent('Olá! Vim pelo site planodeaulapronto.github.io. Estou na página: Plano de Aula Pronto BNCC 2026 — Materiais Pedagógicos para Professores URL: https://planodeaulapronto.github.io/ Gostaria de saber mais sobre este material!') + '" class="whatsapp-float" target="_blank" rel="noopener noreferrer">\n' +
  '    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/></svg>\n' +
  '    Ajuda?\n' +
  '  </a>\n' +
  '  <script>\n' +
  '    let searchIndex = [];\n' +
  '    async function loadAJAXIndex() {\n' +
  '      const t = new Date().getTime();\n' +
  '      console.log("Loading search index v" + t);\n' +
  '      try {\n' +
  '        const [p, a] = await Promise.all([\n' +
  '          fetch(\'search-index-products.json?v=\' + t).then(r => r.json()),\n' +
  '          fetch(\'search-index-articles.json?v=\' + t).then(r => r.ok ? r.json() : [])\n' +
  '        ]);\n' +
  '        searchIndex = [...p, ...a];\n' +
  '        console.log("Search index loaded: " + searchIndex.length + " items");\n' +
  '      } catch(e) { console.error(\'AJAX failed\', e); }\n' +
  '    }\n' +
  '    loadAJAXIndex();\n' +
  '\n' +
  '    function stripHtmlClient(h) {\n' +
  '      if(!h) return ""; \n' +
  '      const d = new DOMParser().parseFromString(h, "text/html");\n' +
  '      return d.body.textContent || "";\n' +
  '    }\n' +
  '\n' +
  '    const sInput = document.getElementById("searchInput");\n' +
  '    const sOverlay = document.getElementById("searchOverlay");\n' +
  '    const sBackdrop = document.getElementById("searchBackdrop");\n' +
  '\n' +
  '    sInput.addEventListener("input", (e) => {\n' +
  '      const q = e.target.value.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").trim();\n' +
  '      if(q.length < 1) {\n' +
  '        sOverlay.style.display = "none";\n' +
  '        sBackdrop.style.display = "none";\n' +
  '        return;\n' +
  '      }\n' +
  '      if(q.length < 2) return;\n' +
  '\n' +
  '      const matches = searchIndex.filter(item => {\n' +
  '        const cleanTitle = stripHtmlClient(item.title).toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "");\n' +
  '        return cleanTitle.includes(q);\n' +
  '      }).slice(0, 15);\n' +
  '\n' +
  '      sOverlay.style.display = "block";\n' +
  '      sBackdrop.style.display = "block";\n' +
  '\n' +
  '      if(matches.length > 0) {\n' +
  '        sOverlay.innerHTML = matches.map(item => {\n' +
  '          const icon = item.type === "article" ? "📰" : "📦";\n' +
  '          const price = item.price ? `<span style="color: #16a34a; font-weight: 800">R$ ${item.price}</span>` : "";\n' +
  '          const titleClean = stripHtmlClient(item.title);\n' +
  '          return `<a href="${item.url}" style="display: flex; align-items: center; gap: 10px; padding: 12px; text-decoration: none; border-bottom: 1px solid #f1f5f9; border-radius: 8px;">\n' +
  '            <span style="font-size: 1.2rem">${icon}</span>\n' +
  '            <div style="flex: 1">\n' +
  '              <div style="font-weight: 700; color: #1a1a2e; font-size: 0.9rem">${titleClean}</div>\n' +
  '              <div style="font-size: 0.75rem; color: #64748b">${item.category || item.type}</div>\n' +
  '            </div>\n' +
  '            ${price}\n' +
  '          </a>`;\n' +
  '        }).join("") + `<div style="text-align: center; padding: 8px; font-size: 0.75rem; color: #94a3b8">Resultados: ${matches.length}</div>`;\n' +
  '      } else {\n' +
  '        sOverlay.innerHTML = \'<div style="padding: 20px; text-align: center; color: #64748b">Nenhum resultado encontrado</div>\';\n' +
  '      }\n' +
  '    });\n' +
  '\n' +
  '    document.addEventListener("click", (e) => {\n' +
  '      if(!sInput.contains(e.target) && !sOverlay.contains(e.target)) {\n' +
  '        sOverlay.style.display = "none";\n' +
  '        sBackdrop.style.display = "none";\n' +
  '      }\n' +
  '    });\n' +
  '  </script>\n</body>\n</html>';

fs.writeFileSync(path.join(__dirname, 'index.html'), html);
console.log('Landing page generated: index.html');

// Export search index for products
const searchIndexProducts = products.map(p => ({
  title: stripHtml(p.title),
  slug: p.slug,
  type: 'product',
  category: categorize(p.slug),
  price: p.price,
  url: `produto/${p.slug}.html`
}));
fs.writeFileSync(path.join(__dirname, 'search-index-products.json'), JSON.stringify(searchIndexProducts));
