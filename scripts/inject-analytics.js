const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const ANALYTICS_SCRIPT = '<script src="/assets/js/blender-analytics.js" defer></script>';
const SKIP_DIRS = new Set(['.git', '.vercel', 'node_modules']);
const SKIP_PATH_PREFIXES = [
  `dashboard${path.sep}`
];

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    const relPath = path.relative(ROOT, fullPath);

    if (entry.isDirectory()) {
      if (!SKIP_DIRS.has(entry.name)) walk(fullPath, files);
      continue;
    }

    if (entry.isFile() && entry.name.endsWith('.html')) {
      files.push({ fullPath, relPath });
    }
  }
  return files;
}

function shouldSkip(relPath, html) {
  if (SKIP_PATH_PREFIXES.some(prefix => relPath.startsWith(prefix))) return true;
  if (/name=["']robots["'][^>]+noindex/i.test(html)) return true;
  if (html.includes('/assets/js/blender-analytics.js')) return true;
  if (!/<\/body>/i.test(html)) return true;
  return false;
}

let injected = 0;
let skipped = 0;

for (const file of walk(ROOT)) {
  const html = fs.readFileSync(file.fullPath, 'utf8');
  if (shouldSkip(file.relPath, html)) {
    skipped += 1;
    continue;
  }

  const updated = html.replace(/<\/body>/i, `  ${ANALYTICS_SCRIPT}\n</body>`);
  fs.writeFileSync(file.fullPath, updated);
  injected += 1;
}

console.log(`Blender analytics injection complete. Injected: ${injected}. Skipped: ${skipped}.`);
