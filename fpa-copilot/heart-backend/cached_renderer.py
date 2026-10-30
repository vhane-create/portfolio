"""One persistent renderer subprocess, with bounded requests and clean shutdown."""
import atexit
import json
from pathlib import Path
import queue
import subprocess
import threading


class CachedRenderer:
    def __init__(self, command, cwd, env, log_path):
        self.command,self.cwd,self.env,self.log_path=command,cwd,env,Path(log_path)
        self.process=None
        self.lock=threading.Lock()
        self.messages=None
        self.log=None
        atexit.register(self.close)

    def _start(self):
        self.log=self.log_path.open('a')
        try:
            self.process=subprocess.Popen(self.command,cwd=self.cwd,env=self.env,stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1)
        except BaseException:
            self.log.close();self.log=None;raise
        self.messages=queue.Queue()
        process,messages=self.process,self.messages
        def read():
            try:
                for line in process.stdout: messages.put(line)
            except (OSError, ValueError):
                pass  # Closing a timed-out process can close this stream first.
            finally: messages.put(None)
        threading.Thread(target=read,daemon=True).start()

    def render(self, identity, timeout=3600):
        with self.lock:
            if self.process is None or self.process.poll() is not None:
                self.close();self._start()
            try:
                self.process.stdin.write(json.dumps({'id':identity})+'\n');self.process.stdin.flush()
                line=self.messages.get(timeout=timeout)
                if line is None: raise RuntimeError('Animation worker stopped. Check '+str(self.log_path))
                data=json.loads(line)
                if data.get('id')!=identity: raise RuntimeError('Animation worker returned a different reply.')
                if not data.get('ok'): raise RuntimeError(data.get('error') or 'Animation failed.')
            except queue.Empty:
                self.close();raise RuntimeError('Animation timed out; worker stopped. Check '+str(self.log_path))
            except BaseException:
                self.close();raise

    def close(self):
        process=self.process;self.process=None
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill();process.wait()
            for stream in (process.stdin,process.stdout):
                if stream: stream.close()
        if self.log is not None: self.log.close();self.log=None
