#!/usr/local/bin/python
__author__ = 'ORyan Hampton'
__email__ = 'oryan.hampton@gmail.com'
__copyright__ = 'Copyright (c) 2020 University of Utah, Marriott Library'
__license__ = 'MIT'
__version__ = "1.0.0"

import AppKit
import subprocess
import plistlib
import objc
import Cocoa
import pathlib
import os
import sys
from AppKit import NSFilenamesPboardType, NSDragOperationNone, NSDragOperationCopy, \
    NSOpenPanel, NSSavePanel, NSURL
    
import Crappy_App_Logic
from nibbler import *
        
def quit():
    print("Quit Application.")
    n.quit()
    
def select_app():
    """
    Collects Data from the selected apps plist
    """
    panel = Cocoa.NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(True)
    panel.setResolvesAliases_(True)

    if(panel.runModal() == Cocoa.NSOKButton):
        pathArray = panel.filenames()
        path = pathlib.Path(pathArray[0])
        
        plistPath = path /'Contents'/'Info.plist'
        infoFile = plistPath
        
        try:
            appSize = subprocess.check_output(['du', '-shg', str(path)]).split()[0].decode('utf-8')
            n.views['appSize'].setStringValue_(str(appSize))
        except Exception as err:
            print(err)
            
        n.views['appLocation'].setStringValue_(str(path))
        
        try:
            plist = str(infoFile)
            with open(plist, 'rb') as f:
                info = plistlib.load(f)
                
            if 'CFBundleName' in info:
                global collectedName
                collectedName = info['CFBundleName']
                n.views['appName'].setStringValue_(collectedName)
            else:
                n.views['appName'].setStringValue_('')
                
            if 'CFBundleShortVersionString' in info:
                global collectedVersion
                collectedVersion= info['CFBundleShortVersionString']
                n.views['appVersion'].setStringValue_(collectedVersion)
            else:
                n.views['appVersion'].setStringValue_('')

            if 'CFBundleIconFile' in info:
                global collectedIcon
                collectedIcon = pathlib.Path(plist).parent / 'Resources' / info['CFBundleIconFile']
                n.views['appIcon'].setStringValue_(str(collectedIcon))
            else:
                n.views['appIcon'].setStringValue_('')

            if 'CFBundleIdentifier' in info:
                global collectedIdentifier
                collectedIdentifier = info['CFBundleIdentifier']
                n.views['appIdentifier'].setStringValue_(collectedIdentifier)
            else:
                n.views['appIdentifier'].setStringValue_('')
                
        except Exception as err:
            print('An Error Occured: {0}'.format(err))
            
def submit_data():
    preScript = n.views['preScript'].stringValue() or None
    postScript = n.views['postScript'].stringValue() or None
    closeScript = n.views['closeScript'].stringValue() or None
    setName = n.views['appName'].stringValue() or None
    collectedIdentifier = n.views['appIdentifier'].stringValue() or None
    collectedIcon = n.views['appIcon'].stringValue() or None
    collectedVersion = n.views['appVersion'].stringValue() or None
    collectedLocation = n.views['appLocation'].stringValue() or None
    collectedSize = n.views['appSize'].stringValue() or None
    
    data = {
    'prescript': preScript,
    'postscript': postScript,
    'closescript' : closeScript,
    'collectedname': collectedName,
    'setname': setName,
    'collectedidentifier': collectedIdentifier,
    'collectedicon': collectedIcon,
    'collectedversion': collectedVersion,
    'collectedlocation': collectedLocation,
    'collectedsize': collectedSize
    }
        # pass information to validate
    if collectedName == None or collectedName == '':
        print('No Name')
        error_window('    No Name Found.    ')
    elif collectedSize == None:
        print('No Size')
        error_window('    No Size Added.    ')
    else:
        try:
            Crappy_App_Logic.main(data)
        except Exception as err:
            print('An Error Occured: {0}'.format(err))
            error_window(err)
    
    
def wait_window():
    dialog = "Launch & then quit application located on image then click 'OK' button."
    title = 'App Playpen Wait'
    if subprocess.check_call("""osascript -e 'display dialog "{0}" with title "{1}" ' """.format(dialog,title), shell=True) == 0:
        return True
    else:
        return False

def error_window(err):
    title = 'App Playpen Error'
    os.system("""osascript -e 'display dialog "{0}" with title "{1}" ' """.format(err, title))
    
def finished_window():
    finish_dialog = "The launcher image creation has completed. It is located on the Desktop, but can be distributed from any folder location."
    title = 'App Playpen Finished'
    os.system("""osascript -e 'display dialog "{0}" with title "{1}" ' """.format(finish_dialog, title))
    
def changeIcon():
    panel = Cocoa.NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setResolvesAliases_(True)

    if(panel.runModal() == Cocoa.NSOKButton):
        pathArray = panel.filenames()
        path = pathlib.Path(pathArray[0])
        
        plistPath = path /'Contents'/'Info.plist'
        collectedIcon = plistPath
        n.views['appIcon'].setStringValue_(str(collectedIcon))
        
def addPreScript():
    panel = Cocoa.NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setResolvesAliases_(True)

    if(panel.runModal() == Cocoa.NSOKButton):
        pathArray = panel.filenames()
        path = pathlib.Path(pathArray[0])
        
        plistPath = path /'Contents'/'Info.plist'
        collectedIcon = plistPath
        n.views['preScript'].setStringValue_(str(collectedIcon))
    

def addPostScript():
    panel = Cocoa.NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setResolvesAliases_(True)

    if(panel.runModal() == Cocoa.NSOKButton):
        pathArray = panel.filenames()
        path = pathlib.Path(pathArray[0])
        
        plistPath = path /'Contents'/'Info.plist'
        collectedIcon = plistPath
        n.views['postScript'].setStringValue_(str(collectedIcon))


def addCloseScript():
    panel = Cocoa.NSOpenPanel.openPanel()
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)
    panel.setResolvesAliases_(True)

    if(panel.runModal() == Cocoa.NSOKButton):
        pathArray = panel.filenames()
        path = pathlib.Path(pathArray[0])
        
        plistPath = path /'Contents'/'Info.plist'
        collectedIcon = plistPath
        n.views['closeScript'].setStringValue_(str(collectedIcon))

    
def main():
    path = AppKit.NSImage.alloc().initByReferencingFile_(os.path.dirname(__file__)+"/App_Playpen_Logo.png")
    n.views['appLogo'].setImage_(path)

    n.attach(select_app, 'SelectApp')
    n.attach(quit, 'quitButton')
    n.attach(submit_data, 'build')
    n.attach(changeIcon, 'changeIcon')
    n.attach(addPreScript, 'addPreScript')
    n.attach(addPostScript, 'addPostScript')
    n.attach(addCloseScript, 'addCloseScript')

    n.hidden = False
    n.run()
    

if __name__ == '__main__':
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = pathlib.Path(dir_path).parent / 'App_Playpen.nib'
        n = Nibbler(dir_path)
    except Exception as err:
        print("Unable to load nib: {0}".format(err))
        sys.exit(20)
    
    main()
