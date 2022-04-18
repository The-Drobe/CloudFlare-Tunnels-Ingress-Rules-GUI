import os
import signal
import subprocess

class main():
    def CloudFlaredTaskMangerStart(self):
        cmd = "cd data && cloudflared tunnel --config config.yml run"
        self.pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 

    def CloudFlaredTaskMangerStop(self):
        os.killpg(os.getpgid(self.pro.pid), signal.SIGTERM)  # Send the signal to all the process groups

# Copyright Giles Wardrobe 2022