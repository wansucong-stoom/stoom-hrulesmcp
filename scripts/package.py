"""Validate and reproducibly package the public installation files."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = 'https://h-rules.stoom.win/api/mcp'
PACKAGES = {
    'stoom-hrules-gpt.zip': ROOT / 'plugins/hannam-regulations-gpt',
    'stoom-hrules-claude.zip': ROOT / 'plugins/hannam-regulations-claude',
    'hannam-regulations-skill.zip': ROOT / 'plugins/hannam-regulations-gpt/skills/hannam-regulations',
    'hannam-regulations-claude-skill.zip': ROOT / 'plugins/hannam-regulations-claude/skills/hannam-regulations',
}


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def validate():
    gpt = load_json('plugins/hannam-regulations-gpt/plugin.json')
    claude = load_json('plugins/hannam-regulations-claude/.claude-plugin/plugin.json')
    assert gpt['version'] == claude['version']
    assert re.fullmatch(r'\d+\.\d+\.\d+', gpt['version'])
    assert gpt['name'] == 'hannam-regulations-gpt'
    assert claude['name'] == 'hannam-regulations-claude'
    assert not set(gpt) & {'skills', 'mcpServers', 'apps', 'interface'}
    assert len(gpt['extensions']['com.openai']['interface']['shortDescription']) <= 30
    for path, expected_type in [('plugins/hannam-regulations-gpt/mcp.json', 'streamable-http'),
                                ('plugins/hannam-regulations-claude/.mcp.json', 'http')]:
        servers = load_json(path)['mcpServers']
        assert servers == {'hannam-regulations': {'type': expected_type, 'url': ENDPOINT}}
    for marketplace_path, plugin_name in [('.agents/plugins/marketplace.json', gpt['name']),
                                          ('.claude-plugin/marketplace.json', claude['name'])]:
        market = load_json(marketplace_path)
        assert market['name'] == 'stoom-hrulesmcp'
        assert len(market['plugins']) == 1
        entry = market['plugins'][0]
        assert entry['name'] == plugin_name
        source = entry['source']
        relative = source['path'] if isinstance(source, dict) else source
        assert relative == './plugins/' + plugin_name
        assert (ROOT / relative).is_dir()
    gpt_skill = ROOT / 'plugins/hannam-regulations-gpt/skills/hannam-regulations'
    claude_skill = ROOT / 'plugins/hannam-regulations-claude/skills/hannam-regulations'
    for folder in (gpt_skill, claude_skill):
        text = (folder / 'SKILL.md').read_text()
        assert re.match(r'^---\nname: hannam-regulations\ndescription: .+\n---\n', text)
        assert len(text.splitlines()) < 500
        for ref in re.findall(r'\]\((references/[^)]+)\)', text):
            assert (folder / ref).is_file(), ref
    for path in gpt_skill.rglob('*.md'):
        # The API reference includes client-specific connection examples.
        if path.name != 'api.md':
            assert path.read_bytes() == (claude_skill / path.relative_to(gpt_skill)).read_bytes()
    metadata = (gpt_skill / 'agents/openai.yaml').read_text()
    assert 'url: "' + ENDPOINT + '"' in metadata
    assert '$hannam-regulations' in metadata
    schema = load_json('plugins/hannam-regulations-gpt/gpts/openapi.json')
    assert schema['servers'] == [{'url': 'https://h-rules.stoom.win'}]
    public_reads = {
        'get_sync_status', 'search_regulations', 'list_regulation_versions',
        'list_articles', 'get_regulation', 'get_article', 'compare_articles',
        'get_knowledge_manifest', 'search_hwiki', 'get_hwiki_page',
    }
    public_writes = {
        '/api/hwiki/drafts': 'submit_hwiki_draft',
        '/api/hwiki/organization/proposals': 'submit_hwiki_organization',
    }
    assert set(schema['paths']) == {'/api/qa/' + name for name in public_reads} | set(public_writes)
    for name in public_reads:
        operation = schema['paths']['/api/qa/' + name]
        assert set(operation) == {'get'}
        assert operation['get']['operationId'] == name
    for route, name in public_writes.items():
        operation = schema['paths'][route]
        assert set(operation) == {'post'}
        assert operation['post']['operationId'] == name
        assert operation['post']['x-openai-isConsequential'] is True
        properties = operation['post']['requestBody']['content']['application/json']['schema']['properties']
        assert 'publication' not in properties
    instruction = ROOT / 'plugins/hannam-regulations-gpt/gpts/instructions.md'
    assert len(instruction.read_text()) < 8000
    for base in (ROOT / 'plugins', ROOT / 'docs'):
        for path in base.rglob('*'):
            assert not path.is_symlink(), path
            if not path.is_file():
                continue
            assert path.suffix in {'.md', '.json', '.yaml'}, path
            assert path.name != '.app.json'
            text = path.read_text()
            assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|plugin_asdk_app_)', text), path
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    target = (path.parent / link.split('#')[0]).resolve()
                    assert target.is_relative_to(ROOT) and target.exists(), (path, link)


def archive_bytes(folder):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(folder.rglob('*'), key=lambda item: item.relative_to(folder).as_posix()):
            assert not path.is_symlink()
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(folder.parent).as_posix(), (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes(), compresslevel=9)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--site-root', type=Path)
    args = parser.parse_args()
    validate()
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    checksums = []
    for name, folder in PACKAGES.items():
        data = archive_bytes(folder)
        path = dist / name
        if args.check:
            assert path.read_bytes() == data, 'Rebuild changed archive: ' + name
        else:
            path.write_bytes(data)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            assert archive.testzip() is None
            assert all(p.startswith(folder.name + '/') and '..' not in Path(p).parts for p in archive.namelist())
            assert len({p.split('/')[0] for p in archive.namelist()}) == 1
        checksums.append(hashlib.sha256(data).hexdigest() + '  ' + name)
    text = '\n'.join(checksums) + '\n'
    if args.check:
        assert (dist / 'SHA256SUMS.txt').read_text() == text
    else:
        (dist / 'SHA256SUMS.txt').write_text(text)
    if args.site_root:
        assert not args.check
        site = args.site_root.resolve()
        assert (site / 'web/connection-guide.html').is_file()
        for name in PACKAGES:
            shutil.copyfile(dist / name, site / 'web' / name)
        shutil.copyfile(dist / 'SHA256SUMS.txt', site / 'web/stoom-hrulesmcp-checksums.txt')
        for name, folder in [( 'hannam-regulations-skill', PACKAGES['hannam-regulations-skill.zip']),
                             ('hannam-regulations-claude-skill', PACKAGES['hannam-regulations-claude-skill.zip'])]:
            shutil.copyfile(folder / 'SKILL.md', site / 'web' / (name + '.md'))
    print('Validated two plugin packages, two skill ZIPs, shared guidance, public-only connections and SHA-256 checksums')


if __name__ == '__main__':
    main()
