"""Clean launcher for ref_burst.py"""
import subprocess
import os

env = os.environ.copy()
# Remove problematic environment variables
env.pop('PYTHONPATH', None)
env.pop('PYTHONHOME', None)

cmd = [
    r'D:\miniconda\envs\bibx\python.exe',
    r'c:\Users\谢\Desktop\vscodepj\文献计量学\图片代码\ref_burst.py'
]

subprocess.run(cmd, env=env)
