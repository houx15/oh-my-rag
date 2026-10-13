"""Explicit audited administrative batch lifecycle; no provider dispatch."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.batch import activate,close_batch


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['activate','close']);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--reason',required=True);p.add_argument('--profile',type=Path);p.add_argument('--root',type=Path);p.add_argument('--name');a=p.parse_args()
    if a.action=='activate':
        if a.profile is None or a.root is None or not a.name:p.error('activation requires --profile --root --name')
        event=activate(profile_path=a.profile,root=a.root,name=a.name,reason=a.reason,output=a.receipt)
    else:event=close_batch(a.receipt,a.reason)
    print(json.dumps(event,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
