#!/usr/local/bin/python3
_author__ = 'ORyan Hampton'
__email__ = 'oryan.hampton@gmail.com'
__copyright__ = 'Copyright (c) 2020 University of Utah, Marriott Library'
__license__ = 'MIT'
__version__ = "1.0.0"

import subprocess
import shutil
import os
import plistlib
import pathlib
from App_Playpen import wait_window, error_window, finished_window, wait_window_blank
import time

VARS = None

class Variables:
    """
    Allows for easy access to the variables needed to create the app wrapper
    """
    def __init__(self, data=None):
        self.data = data or {}

    @property
    def prescript(self):
        return self.data.get('prescript')

    @property
    def setname(self):
        return self.data.get('setname')

    @property
    def closescript(self):
        return self.data.get('closescript')

    @property
    def postscript(self):
        return self.data.get('postscript')

    @property
    def name(self):
        return self.data.get('collectedname')

    @property
    def identifier(self):
        return self.data.get('collectedidentifier')

    @property
    def icon(self):
        return self.data.get('collectedicon')

    @property
    def version(self):
        return self.data.get('collectedversion')

    @property
    def location(self):
        return self.data.get('collectedlocation')

    @property
    def size(self):
        return self.data.get('collectedsize')

    def update(self, data):
        self.data = data


def processHelper(cmd, cwd=None, msg='Error'):
    """
    Used to run subprocess calls with an easy error window throw
    :param cmd:
    :param cwd:
    :param msg:
    :return:
    """
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p_status = process.wait()
    out, err = process.communicate()
    if process.returncode != 0:
        if 'File exists' in str(err):
            fileExists = True
        else:
            print(err)
            error_window(err)
        if 'Resource temporarily unavailable' in str(err):
            time.sleep(5)
            processHelper(cmd,cwd,msg)

    time.sleep(2)

def postcleanup(blank):
    """
    used to clean up the tmp folder and moves finished wrapper to desktop
    :return:
    """
    global VARS
    setname = str(VARS.setname).replace(' ','')
    os.remove(f"/tmp/{setname}.sparseimage")
    os.remove(f"/tmp/{setname}-original.dmg")

    dir_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent.parent

    if blank is True:
        os.remove(dir_path/'temp'/'icon.icns')
    
    try:
        dir_path = dir_path/f"{VARS.setname}.app"
        shutil.move(str(dir_path), str(pathlib.Path.home()/'Desktop'))
    except Exception as err:
        print(f"{err} : Post Cleanup Failed.")
        error_window(err)
    
    
def copyIcon(VARS):
    """
    Copies icon from source application to the wrapper app
    :param VARS:
    :return:
    """
    name = VARS.setname
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent
    dst = f"{dir_path}/{name}.app/Contents/Resources/icon.icns"
    iconPath = pathlib.Path(VARS.icon)
    if iconPath.suffix != '.icns':
        shutil.copy(f"{VARS.icon}.icns", dst)
    else:
        shutil.copy(VARS.icon, dst)
        
def copyIconBlank(VARS):
    """
    Copies icon from source application to the wrapper app
    :param VARS:
    :return:
    """
    name = VARS.setname
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent
    dst = f"{dir_path}/{name}.app/Contents/Resources/icon.icns"
    src = f"{dir_path}/temp/icon.icns"
    try:
        shutil.copy(src, dst)
    except Exception as err:
        error_window(err)

def copyWrapper():
    """
    Copies the template wrapper to the current working directory
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent
    src = pathlib.Path(f"{dir_path}/Reserve/Original-Template.app")
    dst = pathlib.Path(f"{dir_path}/Template.app")
    shutil.copytree(str(src), str(dst))

def moveFiles():
    """
    Moves the dmg files from reserve to the wrapper app
    :return:
    """
    name = VARS.setname.replace(' ','')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent

    sourcePath = pathlib.Path("/tmp")
    source = os.listdir(sourcePath)
    destinationPath = pathlib.Path(f"{dir_path}/Template.app/Contents/Resources/")

    for file in source:
        pathFile = pathlib.Path(file)
        if pathFile.suffix == ".dmg":
            if(pathFile.stem == f"{name}-original"):
                continue
            else:
                shutil.move(sourcePath / pathFile, destinationPath / pathFile)
        elif pathFile.suffix == ".dmgpart":
            shutil.move(sourcePath / pathFile, destinationPath / pathFile)

def changePlist(data):
    """
    Edits the Plist in the wrapper app with the collected information from the original app
    :param data:
    :return:
    """
    name = data.setname
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent
    try:
        plistPath = f"{dir_path}/{name}.app/Contents/Info.plist"
        p = plistlib.readPlist(plistPath)
        p['CFBundleIconFile'] = 'icon'
        p['CFBundleName'] = data.name
        p['CFBundleShortVersionString'] = data.version
        p['CFBundleIdentifier'] = data.identifier
        plistlib.writePlist(p, plistPath)

    except Exception as err:
        print(f"plist change failed: {err}")
        error_window(err)

def copyScripts(data):
    name = data.setname
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent
    preScriptSource = data.prescript
    postScriptSource = data.postscript
    closeScriptSource = data.closescript

    try:
        if preScriptSource != None:
            destPath = f"{dir_path}/{name}.app/Contents/Resources/prescript"
            shutil.copy(str(preScriptSource), str(destPath))

        if postScriptSource != None:
            destPath = f"{dir_path}/{name}.app/Contents/Resources/postscript"
            shutil.copy(str(postScriptSource), str(destPath))

        if closeScriptSource != None:
            destPath = f"{dir_path}/{name}.app/Contents/Resources/closescript"
            shutil.copy(str(closeScriptSource), str(destPath))
    except Exception as err:
        print(err)


def wrapperStarter():
    """
    Initiates the sparseimage
    attaches the sparseimage
    makes the Application Folder in the sparseimage
    :return:
    """
    global VARS
    name = VARS.setname.replace(' ','')
    wrapCMD = ['hdiutil', 'create', '-size', f"{VARS.size}g", '-fs', 'HFS+J', '-type', 'SPARSE', '-volname', name, name]
    processHelper(wrapCMD,'/tmp/', 'Wrapper Creation Failed: ')

    attachCMD = ['hdiutil', 'attach', f"{name}.sparseimage"]
    processHelper(attachCMD, '/tmp/', 'Volume Failed to Attach: ')

    createApplicationVolume = ['mkdir', f"/Volumes/{name}/Applications"]
    processHelper(createApplicationVolume, '/', 'Applications Folder Creation Failed: ')

    try:
        location = pathlib.Path(VARS.location)
        locationName = location.name
        shutil.copytree(VARS.location, f"/Volumes/{name}/Applications/{locationName}")
    except Exception as err:
            doNothing = True
            
def wrapperStarterBlank(name, size):
    """
    Initiates the sparseimage
    attaches the sparseimage
    makes the Application Folder in the sparseimage
    :return:
    """
    name = VARS.setname.replace(' ','')
    wrapCMD = ['hdiutil', 'create', '-size', f"{size}g", '-fs', 'HFS+J', '-type', 'SPARSE', '-volname', name, name]
    processHelper(wrapCMD,'/tmp/', 'Wrapper Creation Failed: ')

    attachCMD = ['hdiutil', 'attach', f"{name}.sparseimage"]
    processHelper(attachCMD, '/tmp/', 'Volume Failed to Attach: ')

    createApplicationVolume = ['mkdir', f"/Volumes/{name}/Applications"]
    processHelper(createApplicationVolume, '/', 'Applications Folder Creation Failed: ')

def finishWrapper(blank):
    """
    Detatches volume,
    converts sparseimage to dmg
    segements the new dmg
    moves dmg files to wrapper
    changes the wrapper name
    copies the icon file
    changes the plist and then cleans up the tmp folder
    :return:
    """
    global VARS
    name = VARS.setname.replace(' ','')

    copyWrapper()

    detachVolumeCMD = ['/usr/bin/hdiutil', 'detach', name]
    processHelper(detachVolumeCMD, cwd='/Volumes', msg='Volume Detach Failure: ')

    convertToDmgCMD = ['/usr/bin/hdiutil', 'convert', f"{name}.sparseimage", '-format', 'UDRO', '-o', f"{name}-original.dmg"]
    processHelper(convertToDmgCMD, cwd='/tmp', msg='Conversion to DMG failed: ')

    segmentCMD = ['/usr/bin/hdiutil', 'segment', '-o', name, '-segmentSize', '1g', f'{name}-original.dmg']
    processHelper(segmentCMD, cwd='/tmp', msg='Segment Failed: ')

    try:
        moveFiles()
    except Exception as err:
        error_window(err)

    changeWrapperName = ['/bin/mv', 'Template.app', f"{VARS.setname}.app"]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = pathlib.Path(dir_path).parent.parent

    processHelper(changeWrapperName, cwd=dir_path, msg='Wrapper Name Change Failed: ')

    # copies icon over to the package
    if blank == False:
        copyIcon(VARS)
    else:
        copyIconBlank(VARS)

    # Changes the Plist in the template with the proper information
    changePlist(VARS)

    #copies over pre, post and exit scripts
    copyScripts(VARS)

    #cleans up tmp dir and moves finished app to Desktop
    postcleanup(blank)

    #Shows Finished Indicator
    finished_window()

def main(data, blank):
    global VARS
    
    if blank == True:
        print('got into blank.')
        VARS = Variables(data)

        wrapperStarterBlank(VARS.setname, VARS.size)
            
        waitCheck = wait_window_blank()
        
        if waitCheck is True:
            path = pathlib.Path(f"/Volumes/{VARS.setname}/Applications")
            appLoc = os.listdir(path)
            for file in appLoc:
                file = pathlib.Path(file)
                if file.suffix == ".app":
                    plistPath = pathlib.Path(f"/Volumes/{VARS.setname}/Applications/{file}/Contents/Info.plist")
                    
                    plist = str(plistPath)
                    with open(plist, 'rb') as f:
                        info = plistlib.load(f)
                        
                        if 'CFBundleIdentifier' in info:
                            collectedIdentifier = info['CFBundleIdentifier'] or None

                        if 'CFBundleName' in info:
                            collectedName = info['CFBundleName'] or None
                        
                        if 'CFBundleIconFile' in info:
                            collectedIcon = info['CFBundleIconFile'] or None
                            dir_path = os.path.dirname(os.path.realpath(__file__))
                            dir_path = pathlib.Path(dir_path).parent.parent
                            dst = pathlib.Path(f"{dir_path}/temp/icon.icns")
                            src = pathlib.Path(f"/Volumes/{VARS.setname}/Applications/{file}/Contents/Resources/{collectedIcon}")
                            iconPath = pathlib.Path(collectedIcon)
                            
                            print(f"Source: {src}")
                            print(f"Destination: {dst}")

                            if iconPath.suffix == ".icns":
                                shutil.copy(src, dst)
                            else:
                                shutil.copy(f"{src}.icns", dst)
                            
                        if 'CFBundleShortVersionString' in info:
                            collectedVersion = info['CFBundleShortVersionString'] or None
                        
                        postScript = VARS.postscript or None
                        preScript = VARS.prescript or None
                        closeScript = VARS.closescript or None
                        
                        data = {
                        'prescript': preScript,
                        'postscript': postScript,
                        'closescript' : closeScript,
                        'setname': VARS.setname,
                        'collectedidentifier': collectedIdentifier,
                        'collectedicon': collectedIcon,
                        'collectedversion': collectedVersion,
                        'collectedname' : collectedName,
                        'collectedlocation': None,
                        'collectedsize': None
                        }
                        
            VARS = Variables(data)
            finishWrapper(True)
            
        else:
            setname = str(VARS.setname).replace(' ','')
            title = 'Error'
            os.remove(f"/tmp/{setname}.sparseimage")
            
            detachVolumeCMD = ['/usr/bin/hdiutil', 'detach', setname]
            processHelper(detachVolumeCMD, cwd='/Volumes', msg='Volume Detach Failure: ')
            
            os.system("""osascript -e 'display dialog "{0}" with title "{1}" ' """.format("Must Choose OK to build image. You must Restart to build image.", title))
    else:
        VARS = Variables(data)
        
        wrapperStarter()
        waitCheck = wait_window()
        
        if waitCheck == True:
            finishWrapper(False)
        else:
            title = 'Error'
            setname = str(VARS.setname).replace(' ','')
            os.remove(f"/tmp/{setname}.sparseimage")
            
            detachVolumeCMD = ['/usr/bin/hdiutil', 'detach', setname]
            processHelper(detachVolumeCMD, cwd='/Volumes', msg='Volume Detach Failure: ')
            
            os.system("""osascript -e 'display dialog "{0}" with title "{1}" ' """.format("Must Choose OK to build image. You must Restart to build image.", title))
            

if __name__ == '__main__':
    data={}
    main(data, False)
