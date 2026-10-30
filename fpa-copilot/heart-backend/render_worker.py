"""Private stdin/stdout render worker; no network listener or speech provider."""
import argparse
from contextlib import redirect_stdout
import hashlib
import json
from pathlib import Path
import re
import sys

APPROVED_SHA='308ab080d0945bb650f905174e716a8a5beecb9b26ec56590aa1aa8ac72839b7'


def serve(incoming, outgoing, upstream, source, audio_dir, output_dir, engine_module=None):
    avatar=None
    if engine_module is None:
        import render_engine as engine_module
    for line in incoming:
        identity=None
        try:
            data=json.loads(line)
            identity=data.get('id') if isinstance(data,dict) else None
            if not isinstance(identity,str) or not re.fullmatch('[a-f0-9]{32}',identity):
                raise ValueError('Invalid render job ID.')
            if hashlib.sha256(source.read_bytes()).hexdigest()!=APPROVED_SHA:
                raise ValueError('Approved facial source differs; stopped.')
            wav=(audio_dir/(identity+'.wav')).resolve()
            if wav.parent!=audio_dir.resolve() or not wav.is_file() or wav.stat().st_size>64*1024**2:
                raise ValueError('Reply WAV is unavailable or invalid.')
            destination=output_dir/(identity+'.mp4')
            if destination.exists(): raise ValueError('Reply output already exists; preserved.')
            with redirect_stdout(sys.stderr):
                if avatar is None: avatar=engine_module.initialize(upstream,source)
                video=engine_module.render(avatar,wav)
            if not video: raise RuntimeError('Renderer returned empty video.')
            with destination.open('xb') as handle: handle.write(video)
            outgoing.write(json.dumps({'id':identity,'ok':True})+'\n');outgoing.flush()
        except Exception as error:
            outgoing.write(json.dumps({'id':identity,'ok':False,'error':str(error)})+'\n');outgoing.flush()
            # A failed GPU operation may leave its runtime unusable. Start fresh
            # on the next request instead of keeping potentially damaged state.
            return 1
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('upstream','source','audio-dir','output-dir'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    paths=[p.resolve() for p in (args.upstream,args.source,args.audio_dir,args.output_dir)]
    if not paths[0].is_dir() or not paths[2].is_dir() or not paths[3].is_dir():
        raise SystemExit('Existing runtime and output folders required.')
    return serve(sys.stdin,sys.stdout,*paths)


if __name__=='__main__': raise SystemExit(main())
