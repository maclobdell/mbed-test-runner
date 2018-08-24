#!/usr/bin/env python
import argparse
import os.path
import subprocess
import datetime
from datetime import datetime
import mbed_lstools
import sys
import json
from os.path import join, abspath, dirname
from json import load, dump
import re
import logging

parser = argparse.ArgumentParser(description='Run Mbed OS tests on all connected boards with all toolchains')
parser.add_argument("-o", "--other_args", default="", action='store', help="Other arguments to pass as a string")  #default is string
parser.add_argument("-d", "--dontrun", default=0, action='count', help="print commands, don't run them")  #just check if present
parser.add_argument("-f", "--folder", default="test_output", action='store', help="Folder to dump test results to")  #default is string

#Warning: Using shell=True can be a security hazard.  Ignoring because I control the command parameters.
#   Used here so I could have the option to pipe output to log file (e.g. command > log.txt).

#TODO - Every time you run this, create a new folder to store results (add the timestamp to the test_output folder)?


def main():
    toolchains = ['gcc_arm', 'arm', 'iar']
    #toolchains = ['gcc_arm']

    args = parser.parse_args()

    other_args = args.other_args
    folder = args.folder

    mbeds = mbed_lstools.create()
    muts = mbeds.list_mbeds(filter_function=None, unique_names=True, read_details_txt=False)

    mo = datetime.now().month
    day = datetime.now().day
    hr = datetime.now().hour
    min = datetime.now().minute
    timestamp =  str(mo) + str(day) + str(hr) + str(min)

    print(module_name + "TIMESTAMP : " + timestamp)

    for mut in muts:
        print(module_name + "FOUND : " + mut['platform_name'])
    for toolchain in toolchains:
        print(module_name + "TOOLCHAIN : "  + toolchain)

# Output files go in folder structure /<test_output>/<mbed_version>/<platform>
    mbed_os_path = os.getcwd()
    print mbed_os_path

    #create directory for output folder here
    try:
        os.stat(folder)
    except:
        os.mkdir(folder)

    log_file_path = mbed_os_path + "/" + folder + "/test_runner_log_" + timestamp + ".txt"
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
    log = logging.getLogger("Test Runner")
    log.setLevel(logging.DEBUG)     
    
    logger("-----------------------------------",log)
    logger("Simple Mbed Test Runner Log",log)
    logger("-----------------------------------",log)
    logger("TIMESTAMP : " + timestamp,log)
    
    for mut in muts:
        logger("PLATFORM : " + mut['platform_name'],log)
    for toolchain in toolchains:
        logger("TOOLCHAIN : "  + toolchain,log)

    logger("Mbed OS Path: " + mbed_os_path,log)    
    logger("Results Path: " + folder,log)
    
    #get the branch name
    output = subprocess.check_output("git rev-parse --abbrev-ref HEAD" , shell=True, stderr=subprocess.STDOUT)    
    
    #TODO - need to add check for mbed-os branch is appropriate to set as folder name.
    mbed_ver = re.sub(r'\W+', '', output)  #remove weird characters
    logger("Mbed OS Ver: " + mbed_ver,log)

    logger("Test Parameters: " + other_args,log)
    logger("-----------------------------------",log)
    
    #change to the output directory
    os.chdir(folder)

    #create directory for the mbed version results
    try:
        os.stat(mbed_ver)
    except:
        os.mkdir(mbed_ver)
        
    os.chdir(mbed_ver)
    
    logger("Testing Started",log)
    logger("Executing Commands...",log)
        
    for mut in muts:
        target = mut['platform_name']

        #create directory for the platform
        try:
            os.stat(target)
        except:
            os.mkdir(target)

        os.chdir(target)
        output_folder_path = os.getcwd()
        log.debug("Results Going To: " + output_folder_path)
        
        #go back up one
        os.chdir("../")

        output_file_name = target + "_" + toolchain + "_" + timestamp + "_results.json"
        
        for toolchain in toolchains:
            test_command = "mbed test --compile " + " -t " + toolchain + " -m " + target + " " + other_args
            logger(test_command,log)

            if args.dontrun == 0:
                try:
                    call_result = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    call_result = str(e.output)
                    log.error("Result: COMPILE COMMAND FAILED " + toolchain + " " + target)
                log.debug("Command Output " + str(call_result))                
            test_command = "mbed test --run " + " -t " + toolchain + " -m " + target + " " + other_args + " --report-json " + output_folder_path + "/" + output_file_name    
            logger(test_command,log)
            if args.dontrun == 0:
                try:
                    call_result = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    call_result = str(e.output)
                    log.error("Result: TEST COMMAND FAILED " + toolchain + " " + target)
                log.debug("Command Output " + str(call_result))

                 
def logger(details, log):
    print(details)
    log.info(details)


if __name__ == '__main__':
    main()
