"""Export only the already-public OpenViST catalogue. Never execute recipe code."""
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ENDPOINT = 'https://openvist.com/wp-json/openvist-recipes/v1/library'
EXTENSIONS = {'python': 'py', 'javascript': 'cjs', 'rust': 'rs'}
FIELDS = ('slug','kind','title','goal','language','version','license','reviewed_at','intro',
          'requirements','limits','steps','checks','usage','example_input','expected_output',
          'tested_scope','sources','projects','provenance')

def digest(value):
    return hashlib.sha256(value).hexdigest()

def collect():
    recipes = []
    for page in range(1,101):
        request = urllib.request.Request(ENDPOINT+'?page='+str(page), headers={'User-Agent':'OpenViST-Public-Library/1.0'})
        with urllib.request.urlopen(request,timeout=30) as response:
            raw = response.read(4_000_001)
        if len(raw)>4_000_000:
            raise ValueError('Catalogue page exceeds limit.')
        value = json.loads(raw)
        if value.get('schema')!='openvist.recipe-catalogue.v1':
            raise ValueError('Unexpected public catalogue schema.')
        recipes.extend(value['recipes'])
        if page>=value['pages']:
            return {'schema':value['schema'],'recipes':recipes}
    raise ValueError('Too many catalogue pages.')

def export(snapshot, root):
    root = Path(root)
    if snapshot.get('schema') != 'openvist.recipe-catalogue.v1' or not snapshot.get('recipes'):
        raise ValueError('Expected a nonempty public catalogue; nothing was written.')
    if len(snapshot['recipes']) > 10000:
        raise ValueError('Catalogue exceeds the export limit.')
    def safe_target(path):
        target = root/path
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
            raise ValueError('Symlink in export path: '+str(path))
        return target
    for name in ('LICENSE', 'README.md', 'catalogue.json', 'THIRD_PARTY_NOTICES.md'):
        safe_target(Path(name))
    license_text = (root/'LICENSE').read_text()
    planned = {}
    index = []
    notices = []
    seen = set()
    for item in snapshot['recipes']:
        record = item['record']
        slug = record['slug']; version = record['version']; language = record.get('language','python')
        if not re.fullmatch(r'[a-z0-9-]{3,80}',slug) or not re.fullmatch(r'\d+\.\d+\.\d+',version) or language not in EXTENSIONS or slug in seen:
            raise ValueError('Invalid or duplicate public identity.')
        seen.add(slug)
        if record.get('license','MIT')!='MIT':
            raise ValueError('Review the recipe license before exporting: '+slug)
        code = item['code'].encode('utf-8')
        if not code or digest(code)!=item['code_sha256']:
            raise ValueError('Public code hash mismatch: '+slug)
        if item['url']!='https://openvist.com/recipes/'+slug+'/':
            raise ValueError('Unexpected public recipe URL.')
        usage = record.get('usage','')
        found = re.search(r'\b([A-Za-z0-9_-]+\.(?:py|cjs|js|rs))\b',usage)
        filename = found.group(1) if found else 'recipe.'+EXTENSIONS[language]
        allowed = {'python':('.py',),'javascript':('.js','.cjs'),'rust':('.rs',)}[language]
        if not filename.endswith(allowed):
            raise ValueError('Usage filename and language differ: '+slug)
        folder = Path('recipes')/language/slug/('v'+version)
        code_path = folder/filename
        metadata = {key:record[key] for key in FIELDS if key in record}
        metadata.update(language=language,license='MIT',url=item['url'],code_file=filename,
                        code_sha256=item['code_sha256'],published_record_sha256=item['record_sha256'])
        planned[code_path] = code
        planned[folder/'recipe.json'] = (json.dumps(metadata,ensure_ascii=False,indent=2)+'\n').encode()
        planned[folder/'LICENSE'] = license_text.encode()
        provenance = record.get('provenance')
        if provenance:
            if provenance.get('license')!='MIT' or not provenance.get('license_notice'):
                raise ValueError('Upstream notice requires review: '+slug)
            notice = ('Adapted source: '+provenance['url']+'\nCommit: '+provenance['commit']+
                '\nLicense choice: '+provenance.get('license_choice','MIT')+'\n\n'+provenance['license_notice'])
            planned[folder/'UPSTREAM-NOTICE.txt'] = notice.encode()
            notices.append('## '+record['title']+'\n\n'+notice+'\n')
        sections = ['# '+record['title'], record['goal'],
            'Published recipe: ['+slug+']('+item['url']+')',
            '**Language:** '+language+' · **Version:** '+version+' · **License:** MIT',
            '## Usage', 'Code file: `'+filename+'`', record.get('usage','See requirements below.')]
        for label,key in [('Requirements','requirements'),('Steps','steps'),('Checks','checks'),('Limits','limits')]:
            if record.get(key):
                sections.extend(['## '+label,'\n'.join('- '+text for text in record[key])])
        for label,key in [('Example input','example_input'),('Expected output','expected_output')]:
            if record.get(key):
                sections.extend(['## '+label,'```text\n'+record[key]+'\n```'])
        sections.extend(['## Recorded validation scope',record['tested_scope'],
            'This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.',
            '## Sources','\n'.join('- '+url for url in record['sources'])])
        if provenance:
            sections.extend(['## Attribution','See UPSTREAM-NOTICE.txt for the original copyright and MIT license notice.'])
        planned[folder/'README.md'] = ('\n\n'.join(sections)+'\n').encode()
        index.append({'slug':slug,'title':record['title'],'language':language,'version':version,
                      'license':'MIT','url':item['url'],'code':code_path.as_posix(),
                      'documentation':(folder/'README.md').as_posix(),
                      'metadata':(folder/'recipe.json').as_posix(),'code_sha256':item['code_sha256']})
    # Validate all collisions before writing any recipe. Published versions are immutable.
    for path,content in planned.items():
        target=safe_target(path)
        if target.is_symlink() or (target.exists() and target.read_bytes()!=content):
            raise ValueError('Existing version differs; review and version it explicitly: '+str(path))
    for path,content in planned.items():
        target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            target.write_bytes(content)
    index.sort(key=lambda item:(item['language'],item['slug'],item['version']))
    (root/'catalogue.json').write_text(json.dumps({'schema':'openvist.public-library.v1','recipes':index},ensure_ascii=False,indent=2)+'\n')
    (root/'THIRD_PARTY_NOTICES.md').write_text('# Third-party notices\n\n'+('\n'.join(notices) or 'No third-party notices in this snapshot.\n'))
    description = ['# OpenViST Recipe Library',
        'Small, documented code examples published on [OpenViST](https://openvist.com/recipes/).',
        'Only publicly published recipes are included. Each version retains its exact code SHA-256, usage, sources, limits and recorded validation scope. No recipe is executed during export.',
        '## Browse']
    table = ['| Language | Recipe | Version |', '| --- | --- | --- |']
    table.extend('| '+row['language']+' | ['+row['title'].replace('|','\\|')+']('+row['documentation']+') | '+row['version']+' |' for row in index)
    description.append('\n'.join(table))
    description += ['', '## Organization', '`recipes/<language>/<slug>/v<version>/` contains the code, README, metadata and license. `catalogue.json` is the machine-readable index.',
        '## License', 'Scripts use MIT, matching the license published by OpenViST. Adapted examples retain their upstream copyright notices beside the code and in THIRD_PARTY_NOTICES.md.',
        '## Before running', 'Read each recipe\'s requirements, limits and source links. Some API examples need your own credentials and can incur provider charges when you run them. Never commit credentials. A recorded test scope is not a guarantee for arbitrary inputs or environments.',
        '## Refresh from published OpenViST recipes', 'Run `python3 tools/export_library.py --output .` from this repository, inspect the diff, and commit the intended additions. Existing published versions are preserved; differing code or documentation requires explicit review.']
    (root/'README.md').write_text('\n\n'.join(description)+'\n')
    return index

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path)
    parser.add_argument('--output',type=Path,default=Path('.'))
    args=parser.parse_args()
    snapshot=json.loads(args.snapshot.read_text()) if args.snapshot else collect()
    index=export(snapshot,args.output)
    print('Public recipes exported:',len(index))

if __name__=='__main__':
    main()
