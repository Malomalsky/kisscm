import os
import re
import sys
import subprocess
import tempfile

sys.stdout.reconfigure(encoding='utf-8')


def cleanup(svg):
    svg = re.sub(r'<\?[^>]*\?>\s*', '', svg)
    svg = re.sub(r'<!DOCTYPE[^>]*(?:\[[\s\S]*?\]\s*)?>\s*', '', svg)
    svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
    svg = re.sub(r'<a\b[^>]*>', '', svg)
    svg = re.sub(r'</a>', '', svg)
    return svg.strip()


def dot(src):
    p = subprocess.run(['dot', '-Tsvg'], input=src.encode('utf8'),
                       capture_output=True)
    print(p.stdout.decode('utf8'))


def plantuml(src):
    p = subprocess.run(['plantuml', '-tsvg', '-pipe'],
                       input=src.encode('utf8'), capture_output=True)
    print(cleanup(p.stdout.decode('utf8')))


def mermaid(src):
    with tempfile.TemporaryDirectory() as path:
        mmd = os.path.join(path, 'diagram.mmd')
        svg = os.path.join(path, 'diagram.svg')
        with open(mmd, 'w', encoding='utf8') as f:
            f.write(src.strip())
        subprocess.run(['mmdc', '-i', mmd, '-o', svg], capture_output=True)
        with open(svg, encoding='utf8') as f:
            print(cleanup(f.read()))
