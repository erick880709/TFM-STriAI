import re
import os

base = r'c:\Users\ELITEBOOK\OneDrive\Documentos\Repositorio\Trabajo\TFM-FINAL\resources\architecture'
md_path = os.path.join(base, 'Documento_Arquitectura_Sistema_Triaje_IA.md')
html_path = os.path.join(base, 'Documento_Arquitectura_Sistema_Triaje_IA.html')

with open(md_path, 'r', encoding='utf-8') as f:
    md = f.read()

# Convert Mermaid code blocks
md = re.sub(r'```mermaid\n(.*?)```', r'<div class="mermaid">\n\1</div>', md, flags=re.DOTALL)

# Build HTML
html = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Documento de Arquitectura — Sistema de Triaje Multimodal IA</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root { --primary: #0891B2; --fg: #164E63; --bg: #F8FAFC; --border: #E2E8F0; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--fg); line-height:1.7; }
.container { max-width: 960px; margin: 0 auto; padding: 24px; }
h1 { font-size: 28px; color: var(--primary); border-bottom: 3px solid var(--primary); padding-bottom: 12px; margin: 32px 0 16px; }
h2 { font-size: 22px; color: var(--primary); margin: 28px 0 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
h3 { font-size: 18px; color: var(--fg); margin: 20px 0 8px; }
h4 { font-size: 15px; color: var(--fg); margin: 16px 0 6px; }
p { margin: 8px 0; }
code { background: #E8F1F6; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
pre { background: #1E293B; color: #E2E8F0; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 12px 0; }
pre code { background: none; padding: 0; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
th { background: var(--primary); color: white; padding: 10px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
tr:nth-child(even) { background: #F8FAFC; }
ul, ol { margin: 8px 0 8px 24px; }
li { margin: 4px 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
.mermaid { background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin: 16px 0; text-align: center; }
strong { color: var(--primary); }
@media print { body { font-size: 11px; } .mermaid { break-inside: avoid; } }
@media (max-width: 600px) { .container { padding: 12px; } table { font-size: 11px; } }
</style>
</head>
<body>
<div class="container">
''' + md + '''
</div>
<script>mermaid.initialize({ startOnLoad: true, theme: "default" });</script>
</body>
</html>'''

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

count = html.count('class="mermaid"')
print(f'HTML generated: {html_path}')
print(f'Mermaid diagrams: {count}')
