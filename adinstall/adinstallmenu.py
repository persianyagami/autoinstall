# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 12:07:28 2017

@author: AJANETT
"""

# Import the modules needed to run the script.
import sys, os
import subprocess
import os.path
from time import sleep
import platform
import json

class Repository:

    #constructor
    def __init__(self, name, giturl, server):
        self.name = name
        self.giturl = giturl
        self.server = server
        
    #pull method -- git clone if the repo doesn't exist locally; error message if it does exist locally
    def pull(self):
        out = subprocess.check_output('test -e %s && echo -n True || echo -n False' % self.name, shell=True)
        out_bool = out.lower() in ("true")
        if out_bool:
            print 'Directory already exists. Running "git pull"...'
            subprocess.call('git pull', shell=True, cwd=self.name)
        else:
            subprocess.call('git clone %s' % self.giturl, shell=True)

    #install method -- run npm install
    def install(self):
        subprocess.call(['npm','install'], cwd=self.name)

    #configure method -- use HashConfig
    def configure(self, configfile = 'config.json_TEMPLATE'):
        conf = True
        while conf == True:
            ans = raw_input('Do you want to edit the configuration file for %s? (y/n)' % self.name)
            if ans == 'y':
                print 'Please follow prompts to generate the configuration file...'
                if configfile == 'config.json_TEMPLATE':
                    subprocess.call(['rm', 'config.json_TEMPLATE'], cwd = hashconfig.name)
                    subprocess.call(['cp', self.name + '/config.json_TEMPLATE', 'hashconfig/config.json_TEMPLATE'])
                    subprocess.call(['node','hconfig.js'], cwd= hashconfig.name)
                    subprocess.call(['mv','config_new.json','config.json'], cwd = hashconfig.name)
                    subprocess.call(['cp', 'hashconfig/config.json', self.name + '/config.json'])
                else:
                    filename = os.path.splitext(configfile)[0]
                    subprocess.call(['rm', 'config.json_TEMPLATE'], cwd = hashconfig.name)
                    subprocess.call(['cp', self.name + '/' + configfile, 'hashconfig/config.json_TEMPLATE'])
                    subprocess.call(['node','hconfig.js'],cwd=hashconfig.name)
                    subprocess.call(['cp', 'hashconfig/config_new.json', self.name+'/'+filename+'.json'])
                conf = False
            elif ans == 'n':
                print 'Skipping configuration editing process...'
                conf = False
            else:
                print 'Invalid input. Must enter "y" or "n".'

 
# Initialize menu options and process.json
menu_actions  = {} 
process = {}
process['apps'] = []
 
 
# =======================
#     MENUS FUNCTIONS
# =======================
 
# Main menu
def main_menu():   
    print "Please choose one of the following options:"
    print "1. Install ACE Direct"
    print "2. Install ACR-CDR"
    print "3. Install Management Portal"
    print "\n0. Finish installation process"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return
 
# Execute menu
def exec_menu(choice):
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return
 
# Menu 1
def acedirectinstall():
    acedirect = Repository('acedirect','https://github.com/mitrefccace/acedirect.git','adserver.js')
    print "Installing ACE Direct \n"
    acedirect.pull()
    subprocess.call(['npm', 'install', '-g', 'bower'])
    subprocess.call(['npm','install','pm2','-g'])
    subprocess.call(['bower', 'install', '--allow-root'], cwd = acedirect.name)
    acedirect.install()
    acedirect.configure()
    process['apps'].append({  
        'name': 'acedirect',
        'script': './acedirect/adserver.js',
        'cwd': './acedirect'
    })
    print "ACE Direct installation complete. Returning to main menu..."
    sys.stdout.flush()
    sleep(2)
    menu_actions['main_menu']()
    return
 
 
# Menu 2
def acrcdrinstall():
    acrcdr = Repository('acr-cdr', 'https://github.com/mitrefccace/acr-cdr.git','app.js')
    print "Installing ACR-CDR \n"
    acrcdr.pull()
    acrcdr.install()
    acrcdr.configure()
    process['apps'].append({  
        'name': 'acrcdr',
        'script': './acr-cdr/app.js',
        'cwd': './acr-cdr'
    })
    print "ACR-CDR installation complete. Returning to main menu..."
    sys.stdout.flush()
    sleep(2)
    menu_actions['main_menu']()
    return
 
# Back to main menu
def mgmtinstall():
    mgmt = Repository('managementportal','https://github.com/mitrefccace/managementportal.git','server-db.js')
    mgmt.pull()
    mgmt.install()
    subprocess.call(['bower', 'install', '--allow-root'], cwd = mgmt.name)
    mgmt.configure()
    process['apps'].append({  
        'name': 'mgmt',
        'script': './managementportal/server-db.js',
        'cwd': './managementportal'
    })
    print "Management portal installation complete. Returning to main menu..."
    sys.stdout.flush()
    sleep(2)
    menu_actions['main_menu']()
    return
 
# Exit program
def finish():
    print 'Writing process.json and starting servers of the installed components...'
    with open('process.json', 'w') as outfile:  
        json.dump(process, outfile)
    subprocess.call(['pm2','start','process.json'])
    sys.exit()

    
# =======================
#    MENUS DEFINITIONS
# =======================

# Menu definition
menu_actions = {
    'main_menu': main_menu,
    '1': acedirectinstall,
    '2': acrcdrinstall,
    '3': mgmtinstall,
    '0': finish,
}
 
# =======================
#      MAIN PROGRAM
# =======================
 
# Main Program
if __name__ == "__main__":
    #check operating system
    if platform.system() != 'Linux':
        print 'Installation script can only be run on Linux. Terminating...'
        quit()
    #check distribution    
    dist = platform.dist()[0]
    if dist != 'centos' and dist != 'redhat':
        print 'Installation script can only be run on CentOS or RedHat. Terminating...'
        quit()
    #stop all processes
    subprocess.call(['pm2','kill'])
    #set up hashconfig
    print 'Installing HashConfig tool for configuration process...'
    hashconfig = Repository('hashconfig','https://github.com/mitrefccace/hashconfig.git','hconfig.js')
    hashconfig.pull()
    hashconfig.install()
    print 'HashConfig installation complete.'
    sys.stdout.flush()
    sleep(2)
    # Launch main menu
    main_menu()