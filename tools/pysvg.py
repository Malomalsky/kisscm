import os
import re
import shutil
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


def check(p):
    if p.returncode != 0:
        msg = p.stderr.decode('utf8') or p.stdout.decode('utf8')
        raise RuntimeError(msg)
    return p.stdout.decode('utf8')


def dot(src):
    p = subprocess.run(['dot', '-Tsvg'], input=src.encode('utf8'),
                       capture_output=True)
    print(p.stdout.decode('utf8'))


def plantuml(src):
    src = src.strip()
    if not src.startswith('@start'):
        src = f'@startuml\n{src}\n@enduml\n'

    jar = os.path.join(os.path.dirname(__file__), 'plantuml.jar')
    if shutil.which('plantuml'):
        cmd = ['plantuml', '-tsvg', '-pipe']
    elif os.path.exists(jar):
        cmd = ['java', '-jar', jar, '-tsvg', '-pipe']
    else:
        raise RuntimeError('plantuml not found')

    p = subprocess.run(cmd, input=src.encode('utf8'), capture_output=True)
    print(cleanup(check(p)))


def mermaid(src):
    mmdc = shutil.which('mmdc')
    if not mmdc:
        raise RuntimeError('mmdc not found')

    with tempfile.TemporaryDirectory() as path:
        mmd = os.path.join(path, 'diagram.mmd')
        svg = os.path.join(path, 'diagram.svg')
        pptr = os.path.join(path, 'puppeteer.json')
        with open(mmd, 'w', encoding='utf8') as f:
            f.write(src.strip())
        with open(pptr, 'w', encoding='utf8') as f:
            f.write('{"args":["--no-sandbox"]}')
        p = subprocess.run([mmdc, '-i', mmd, '-o', svg, '-p', pptr],
                           capture_output=True)
        check(p)
        with open(svg, encoding='utf8') as f:
            print(cleanup(f.read()))
