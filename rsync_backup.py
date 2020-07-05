#!/usr/bin/env python3
import toml
import sys
import subprocess
import os
from datetime import datetime

class AttrDict(dict):
    def __init__(self,*args,**kwargs):
        super(AttrDict,self).__init__(*args,**kwargs)
        self.__dict__=self

cfg_name=sys.argv[1] if len(sys.argv)>1 else 'config.toml'
cfg=toml.load(cfg_name,AttrDict)

now=datetime.now()

os.makedirs(cfg.config.log_dest,exist_ok=True)
with open(cfg.config.log_dest+now.strftime(r"/backup-%Y%m%d-%H%M%S.log"),'w') as log:
    for src_id in cfg.source:
        src=cfg.source[src_id]

        print("===== rsync",src_id)
        print("===== rysnc",src_id,file=log)

        try:
            args=["rsync"]
            args.append('-az')
            args.append('--delete-after')
            args.append('--delete-excluded')
            args.append('--compress-level=9')
            args.append('--delay-updates')
            args.append('--cvs-exclude')
            args.append('--fuzzy')
            args.append('--stats')
            if 'exclude' in src:
                args.append('--exclude-from='+src.exclude)

            # args.append("--progress") # use this while testing
            # args.append("--itemize-changes") # or this one - very chatty as well

            args.extend(['-e','{0} -p {1} -i {2} -o PasswordAuthentication=no -o StrictHostKeyChecking=no'.format(cfg.config.get('ssh','ssh'),src.get('port',23),src.ssh_key)])
            args.append('{0}@{1}:{2}/'.format(src.get('user','root'),src.host,src.path))
            dest='{0}/{1}'.format(cfg.config.rsync_dest,src.id)
            os.makedirs(dest,exist_ok=True)
            args.append(dest)

            log.flush()
            rsync=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
            if rsync.returncode and rsync.returncode!=24: # 24: vanished source files
                print("***** failed, return code",rsync.returncode,file=log)
                continue

            print('----- rsync successful',file=log)

        except Exception as e:
            print("*****",e,file=log)
            print(e)
