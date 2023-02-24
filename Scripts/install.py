import subprocess
import platform
import shutil
import os.path
import stat
import sys
import os

# WINDOWS Installation config
REPO_URL="https://github.com/AdityaP1502/fft-c"
branch = "Windows"
SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
ROOT_PATH = os.path.join(SCRIPT_PATH, "..")
INSTALL_DIR= os.path.abspath(f"{ROOT_PATH}/libs")

def run_command(cmd):
  p = subprocess.Popen(cmd);  
  res = p.communicate()
  
  retcode = p.returncode
  if retcode != 0:
    raise subprocess.CalledProcessError(returncode=retcode, cmd=" ".join(cmd), stderr=res[1])

def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)
    
if __name__ == "__main__":
  try:
    if platform.system() == "Linux":
      run_command("source scripts/install.sh")
      sys.exit(0)
    
    os.chdir(INSTALL_DIR)
    
    run_command("git clone {} --branch {}".format(REPO_URL, branch))
    os.chdir(os.path.join(INSTALL_DIR, "fft-c"))
    
    print("Compiling...")
    run_command(cmd="python scripts/install.py")
    
    shutil.copytree(src=os.path.abspath("dll"), dst=os.path.join(INSTALL_DIR, "shared"))
    shutil.copy("dll/conv.dll", dst=os.path.join(INSTALL_DIR, "shared", "conv.dll"))
    
    os.chdir(INSTALL_DIR)
    shutil.rmtree(os.path.join(INSTALL_DIR, "fft-c"), onerror=on_rm_error)
    
    os.chdir(ROOT_PATH)
    print("OK")
    
  except BaseException as e:
    print(e)
    print("FAIL")
    print(os.path.join(INSTALL_DIR, "fft-c"))
    try:
      if os.path.isdir(os.path.join(INSTALL_DIR, "fft-c")):
        shutil.rmtree(os.path.join(INSTALL_DIR, "fft-c"), onerror=on_rm_error)
    except:
      sys.exit(1)
  
