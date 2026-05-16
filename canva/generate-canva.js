const fs = require('fs');
const path = require('path');

// Read the original generated index.html
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

// Replace all local image paths (images/slug.ext) with public URLs
const canvaHtml = html.replace(/src="images\/([^"]+)"/g, (match, filename) => {
    return `src="../images/${filename}"`;
});

// Create canva directory
const canvaDir = path.join(__dirname);
if (!fs.existsSync(canvaDir)) fs.mkdirSync(canvaDir, { recursive: true });

fs.writeFileSync(path.join(canvaDir, 'index.html'), canvaHtml);

const count = (canvaHtml.match(/diariodaeducacao\.com\.br\/images/g) || []).length;
console.log(`Canva version created: canva/index.html`);
console.log(`Replaced ${count} image URLs to public URLs`);
console.log(`File size: ${(Buffer.byteLength(canvaHtml) / 1024).toFixed(0)} KB`);
