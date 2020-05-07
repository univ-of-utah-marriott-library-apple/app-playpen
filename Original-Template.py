#!/usr/local/bin/python3
_author__ = 'ORyan Hampton'
__email__ = 'oryan.hampton@gmail.com'
__copyright__ = 'Copyright (c) 2020 University of Utah, Marriott Library'
__license__ = 'MIT'
__version__ = "1.0.0"

import psutil
import os
import pathlib
import subprocess
import time

def checkForApplication(processName):
    for process in psutil.process_iter():
        if process is not None:
            try:
                if processName.lower() in process.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        else:
            return False
    return False

def getName():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path)
    dmg_path = dir_path
    source = os.listdir(dmg_path)

    for file in source:
        file = pathlib.Path(file)
        if file.suffix == '.dmg':
            return file.stem

def getFilePath():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path)
    dmg_path = dir_path
    source = os.listdir(dmg_path)

    for file in source:
        file = pathlib.Path(file)
        if file.suffix == '.dmg':
            return str(dmg_path/file)

def launchApplication(name):
    print('Launching Application')
    mount_root = '/Volumes'
    home = pathlib.Path.home()
    shadow_path = home/'Library'/'Application Support'/name
    shadow_file = str(shadow_path/f"{name}.shadow")
    image_path = getFilePath()

    cmd = ['hdiutil', 'attach', '-nobrowse', '-noautoopenro', '-noverify', '-mountroot', mount_root,'-shadow', shadow_file, image_path]
    print(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    out, err = process.communicate()
    print(err)

def shadowFileCreate(name):
    home = pathlib.Path.home()
    shadowPath = home/'Library'/'Application Support'/ name
    os.mkdir(str(shadowPath))

def shadowFileCheck(name):
    print('Starting Shadow File')
    home = pathlib.Path.home()
    shadowPath = home/'Library'/'Application Support'/name
    return shadowPath.exists()

def openForUser(name):
    mount_root = pathlib.Path('/Volumes')
    app_path = mount_root/name/'Applications'
    
    if app_path.exists():
        source = os.listdir(app_path)
        for file in source:
            pathFile = pathlib.Path(file)
            if pathFile.suffix == ".app":
                path = mount_root/name/'Applications'/pathFile
                cmd = ['open', str(path)]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.wait()
                out, err = process.communicate()
        
        
def checkForPreScript():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path)
    dmg_path = dir_path / 'prescript'
    source = os.listdir(dmg_path)
    
    for file in source:
        process = subprocess.call(file)
        process.wait()

def checkForPostScript():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path)
    dmg_path = dir_path / 'postscript'
    source = os.listdir(dmg_path)
    
    for file in source:
        process = subprocess.call(file)
        process.wait()
        
def checkForCloseScript():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path)
    dmg_path = dir_path / 'closescript'
    source = os.listdir(dmg_path)
    
    for file in source:
        process = subprocess.call(file)
        process.wait()
    

def main():
    app_name = getName()
    
    if checkForApplication(app_name):
        print('Application is Running!')
    else:
        if shadowFileCheck(app_name) == False:
            shadowFileCreate(app_name)

        launchApplication(app_name)
        checkForPreScript()
        openForUser(app_name)
        checkForPostScript()
        time.sleep(5)
        
    while checkForApplication(app_name) == True:
        time.sleep(5)
    
    shadow_path = pathlib.Path.home()/'Library'/'Application Support'/app_name
    cmd = ['rm', '-rf', shadow_path]
    process = subprocess.Popen(cmd)
    process.wait()
    
    checkForCloseScript()
    detachVolume = ['hdiutil', 'detach', f"/Volumes/{app_name}"]
    detach = subprocess.Popen(detachVolume)
    detach.wait()


if __name__ == '__main__':
    main()
