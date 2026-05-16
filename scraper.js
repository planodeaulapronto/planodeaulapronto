const https = require('https');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://planodeaulapronto.github.io';
const PRODUCTS_FILE = path.join(__dirname, 'products.json');

function fetch(url, retries = 3) {
    return new Promise((resolve, reject) => {
        const attempt = (n) => {
            const req = https.get(url, {
                headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
                timeout: 20000
            }, (res) => {
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                    const loc = res.headers.location.startsWith('http') ? res.headers.location : BASE_URL + res.headers.location;
                    res.resume();
                    return fetch(loc, n).then(resolve).catch(reject);
                }
                if (res.statusCode !== 200) {
                    res.resume();
                    if (n > 0) { setTimeout(() => attempt(n - 1), 1000); return; }
                    reject(new Error(`HTTP ${res.statusCode}`));
                    return;
                }
                const chunks = [];
                res.on('data', chunk => chunks.push(chunk));
                res.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
            });
            req.on('error', (err) => {
                if (n > 0) { setTimeout(() => attempt(n - 1), 1000); return; }
                reject(err);
            });
            req.on('timeout', () => {
                req.destroy();
                if (n > 0) { setTimeout(() => attempt(n - 1), 1000); return; }
                reject(new Error('timeout'));
            });
        };
        attempt(retries);
    });
}

function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        if (fs.existsSync(dest)) { resolve(true); return; }
        const file = fs.createWriteStream(dest);
        const req = https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 20000 }, (res) => {
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                file.close();
                try { fs.unlinkSync(dest); } catch (e) { }
                const loc = res.headers.location.startsWith('http') ? res.headers.location : BASE_URL + res.headers.location;
                return downloadFile(loc, dest).then(resolve).catch(reject);
            }
            if (res.statusCode !== 200) {
                file.close();
                try { fs.unlinkSync(dest); } catch (e) { }
                reject(new Error(`HTTP ${res.statusCode}`));
                return;
            }
            res.pipe(file);
            file.on('finish', () => { file.close(); resolve(true); });
        });
        req.on('error', (err) => {
            file.close();
            try { fs.unlinkSync(dest); } catch (e) { }
            reject(err);
        });
        req.on('timeout', () => {
            req.destroy();
            file.close();
            try { fs.unlinkSync(dest); } catch (e) { }
            reject(new Error('timeout'));
        });
    });
}

async function getSitemapUrls() {
    console.log('Fetching sitemap...');
    const xml = await fetch(BASE_URL + '/sitemap-pacotes.xml');
    const urls = [];
    const locRegex = /<loc>(https:\/\/diariodaeducacao\.com\.br\/pacote\/[^<]+)<\/loc>/g;
    let m;
    while ((m = locRegex.exec(xml)) !== null) {
        // Skip the /pacotes main page
        if (!m[1].endsWith('/pacotes') && m[1] !== BASE_URL + '/pacotes') {
            urls.push(m[1].endsWith('/') ? m[1] : m[1] + '/');
        }
    }
    console.log(`Found ${urls.length} product URLs in sitemap`);
    return urls;
}

async function enrichProduct(url) {
    const slug = url.replace(BASE_URL + '/pacote/', '').replace(/\/$/, '');
    const product = {
        slug,
        title: '',
        link: url,
        image: '',
        hotmartLink: '',
        description: '',
        price: '',
        discount: '',
        localImage: ''
    };

    try {
        const html = await fetch(url);

        // Title
        const ogTitle = html.match(/<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']+)["']/i);
        const titleTag = html.match(/<title>([^<]+)<\/title>/i);
        const h1Tag = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
        product.title = (ogTitle ? ogTitle[1] : (h1Tag ? h1Tag[1] : (titleTag ? titleTag[1] : '')))
            .replace(/\s*[|\-–]\s*(?:Diário da Educação|Planos de Aula BNCC).*/i, '')
            .replace(/ - Planos de Aula BNCC \d+/i, '')
            .trim() || slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        // Image - try multiple sources
        const ogImg = html.match(/<meta[^>]*property=["']og:image["'][^>]*content=["']([^"']+)["']/i);
        const imgM = html.match(/src=["'](\/images\/produtos-bncc\/[^"']+)["']/);
        const imgM2 = html.match(/src=["'](\/images\/[^"']+)["']/);
        if (ogImg && ogImg[1].includes('/images/')) {
            product.image = ogImg[1].startsWith('http') ? ogImg[1] : BASE_URL + ogImg[1];
        } else if (imgM) {
            product.image = BASE_URL + imgM[1];
        } else if (imgM2) {
            product.image = BASE_URL + imgM2[1];
        } else {
            product.image = `${BASE_URL}/images/produtos-bncc/${slug}.webp`;
        }

        // Description
        const ogDesc = html.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']+)["']/i);
        const metaDesc = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["']/i);
        product.description = (ogDesc ? ogDesc[1] : (metaDesc ? metaDesc[1] : '')).trim();

        // Hotmart link
        const hmM = html.match(/href=["'](https:\/\/go\.hotmart\.com\/[^"']+)["']/);
        if (hmM) product.hotmartLink = hmM[1];

        // Price
        const priceAll = html.match(/R\$\s*([\d]+[.,]\d{2})/g);
        if (priceAll && priceAll.length > 0) {
            // Get the last price (typically the final/discounted price)
            product.price = priceAll[priceAll.length - 1].replace('R$ ', '').replace('R$', '').trim();
        }

        // Discount
        const discM = html.match(/-(\d+)%/);
        if (discM) product.discount = discM[1];

    } catch (err) {
        console.error(`  ERROR: ${slug}: ${err.message}`);
        product.title = product.title || slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        product.image = `${BASE_URL}/images/produtos-bncc/${slug}.webp`;
    }

    return product;
}

async function main() {
    const urls = await getSitemapUrls();

    // Load existing progress if available
    let existingProducts = [];
    if (fs.existsSync(PRODUCTS_FILE)) {
        try {
            existingProducts = JSON.parse(fs.readFileSync(PRODUCTS_FILE, 'utf8'));
            console.log(`Loaded ${existingProducts.length} existing products`);
        } catch (e) { }
    }
    const existingMap = new Map(existingProducts.filter(p => p.title && p.title.length > 3).map(p => [p.slug, p]));

    // Process products one at a time to avoid overwhelming the server
    const allProducts = [];

    for (let i = 0; i < urls.length; i++) {
        const url = urls[i];
        const slug = url.replace(BASE_URL + '/pacote/', '').replace(/\/$/, '');

        // Use existing data if available
        if (existingMap.has(slug) && existingMap.get(slug).hotmartLink) {
            allProducts.push(existingMap.get(slug));
            continue;
        }

        const product = await enrichProduct(url);
        allProducts.push(product);

        if ((i + 1) % 10 === 0) {
            console.log(`  Processed ${i + 1}/${urls.length}: ${product.title.substring(0, 50)}...`);
            // Save progress
            fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(allProducts.concat(urls.slice(i + 1).map(u => ({
                slug: u.replace(BASE_URL + '/pacote/', '').replace(/\/$/, ''),
                title: '', link: u, image: '', hotmartLink: '', description: '', price: '', discount: '', localImage: ''
            }))), null, 2));
        }

        // Small delay
        await new Promise(r => setTimeout(r, 400));
    }

    // Save complete products
    fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(allProducts, null, 2));
    console.log(`\nSaved ${allProducts.length} products to products.json`);

    // Download images
    const imagesDir = path.join(__dirname, 'images');
    if (!fs.existsSync(imagesDir)) fs.mkdirSync(imagesDir);

    let downloaded = 0, failed = 0, skipped = 0;
    console.log(`\nDownloading images...`);

    for (let i = 0; i < allProducts.length; i++) {
        const product = allProducts[i];
        if (!product.image) { failed++; continue; }

        const ext = path.extname(product.image.split('?')[0]) || '.webp';
        const filename = product.slug + ext;
        const dest = path.join(imagesDir, filename);
        product.localImage = `images/${filename}`;

        if (fs.existsSync(dest) && fs.statSync(dest).size > 100) {
            skipped++;
            continue;
        }

        try {
            await downloadFile(product.image, dest);
            downloaded++;
        } catch (err) {
            // Try webp extension
            try {
                const altDest = path.join(imagesDir, product.slug + '.webp');
                await downloadFile(`${BASE_URL}/images/produtos-bncc/${product.slug}.webp`, altDest);
                product.localImage = `images/${product.slug}.webp`;
                downloaded++;
            } catch (e) {
                failed++;
            }
        }

        if ((i + 1) % 20 === 0) {
            console.log(`  Images ${i + 1}/${allProducts.length}: ${downloaded} new, ${skipped} cached, ${failed} failed`);
        }

        await new Promise(r => setTimeout(r, 200));
    }

    // Final save with local image paths
    fs.writeFileSync(PRODUCTS_FILE, JSON.stringify(allProducts, null, 2));

    // Summary
    const withTitle = allProducts.filter(p => p.title && p.title.length > 3).length;
    const withImage = allProducts.filter(p => p.localImage).length;
    const withDesc = allProducts.filter(p => p.description && p.description.length > 10).length;
    const withHotmart = allProducts.filter(p => p.hotmartLink).length;

    console.log(`\n========== SCRAPING COMPLETE ==========`);
    console.log(`Total products:    ${allProducts.length}`);
    console.log(`With titles:       ${withTitle}`);
    console.log(`With local images: ${withImage}`);
    console.log(`With descriptions: ${withDesc}`);
    console.log(`With hotmart links:${withHotmart}`);
    console.log(`Images: ${downloaded} new + ${skipped} cached, ${failed} failed`);
    console.log(`Data saved to products.json`);
    console.log(`=======================================`);
}

main().catch(err => console.error('Fatal error:', err));
