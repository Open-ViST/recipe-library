"""Synchronize the public library from an authorized VPS using one repo deploy key."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys

HTTPS_REPO = 'https://github.com/Open-ViST/recipe-library.git'
SSH_REPO = 'git@github.com:Open-ViST/recipe-library.git'
PATHS = ['recipes', 'catalogue.json', 'README.md', 'THIRD_PARTY_NOTICES.md']


def git(checkout, *args, env=None, capture=False):
    return subprocess.run(['git','-C',str(checkout),*args],check=True,
        env=env, text=True, capture_output=capture, timeout=120)


def synchronize(checkout, key):
    checkout, key = Path(checkout).expanduser().absolute(), Path(key).expanduser().absolute()
    if not key.is_file() or key.is_symlink() or key.stat().st_mode & 0o077:
        raise ValueError('Deploy key must be a regular private file with mode 0600')
    if checkout.is_symlink() or any(p.is_symlink() for p in checkout.parents):
        raise ValueError('Checkout path must not contain symlinks')
    if not checkout.exists():
        checkout.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','clone','--depth','1','--branch','main',HTTPS_REPO,str(checkout)],check=True,timeout=120)
    if git(checkout,'remote','get-url','origin',capture=True).stdout.strip()!=HTTPS_REPO:
        raise ValueError('Unexpected checkout remote')
    if git(checkout,'branch','--show-current',capture=True).stdout.strip()!='main':
        raise ValueError('Expected the main branch')
    if git(checkout,'status','--porcelain',capture=True).stdout.strip():
        raise ValueError('Checkout has local changes; inspect before retrying')
    git(checkout,'pull','--ff-only','origin','main')
    if git(checkout,'rev-list','--count','origin/main..HEAD',capture=True).stdout.strip()!='0':
        raise ValueError('An unpublished local commit remains; reconcile it before retrying')
    subprocess.run([sys.executable,str(checkout/'tools/export_library.py'),'--output',str(checkout)],check=True,timeout=300)
    git(checkout,'add','--',*PATHS)
    changed=subprocess.run(['git','-C',str(checkout),'diff','--cached','--quiet'],timeout=30)
    if changed.returncode==0:
        print('PUBLIC LIBRARY UP TO DATE')
        return
    if changed.returncode!=1:
        raise ValueError('Unable to inspect staged changes')
    git(checkout,'-c','user.name=OpenViST Library Bot','-c','user.email=library-bot@users.noreply.github.com',
        'commit','-m','Sync published OpenViST recipes')
    env=dict(os.environ)
    env['GIT_SSH_COMMAND']='ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -i '+shlex.quote(str(key))
    git(checkout,'push',SSH_REPO,'HEAD:main',env=env)
    print('PUBLIC RECIPES SYNCHRONIZED')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout',type=Path,default=Path.home()/'openvist/public-recipe-library')
    parser.add_argument('--key',type=Path,default=Path.home()/'.ssh/openvist_recipe_library')
    args=parser.parse_args()
    try:
        synchronize(args.checkout,args.key)
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print('SYNC STOPPED:',str(error),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
