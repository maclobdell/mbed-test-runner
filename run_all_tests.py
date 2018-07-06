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

#this script must run in a mbed-os top level directory
ROOT = "."
sys.path.insert(0, ROOT)
from tools.targets import TARGETS

parser = argparse.ArgumentParser(description='Run Mbed OS tests on all connected boards with all toolchains')
parser.add_argument("-o", "--other_args", default="", action='store', help="Other arguments to pass as a string")  #default is string
parser.add_argument("-d", "--dontrun", default=0, action='count', help="print commands, don't run them")  #just check if present
parser.add_argument("-f", "--folder", default="test_output", action='store', help="Folder to dump test results to")  #default is string
parser.add_argument("-s", "--scorecard", default=0, action='count', help="generate scorecard file")  #just check if present

#Warning: Using shell=True can be a security hazard.  Ignoring because I control the command parameters.
#   Used here so I could have the option to pipe output to log file (e.g. command > log.txt).

def main():
    module_name = "[run_all_tests.py] : "

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
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)     
    
    #get the branch name
    output = subprocess.check_output("git rev-parse --abbrev-ref HEAD" , shell=True, stderr=subprocess.STDOUT)    
    
    #todo - need to add check for mbed-os branch is appropriate to set as folder name.
    output_alnum = re.sub(r'\W+', '', output)
    log.debug(output_alnum)
    mbed_ver = output_alnum
    
    #change to the output directory
    os.chdir(folder)

    #create directory for the mbed version results
    try:
        os.stat(mbed_ver)
    except:
        os.mkdir(mbed_ver)
        
    os.chdir(mbed_ver)
    
    for mut in muts:
        target = mut['platform_name']

        #create directory for the platform
        try:
            os.stat(target)
        except:
            os.mkdir(target)

        os.chdir(target)
        output_folder_path = os.getcwd()
        log.debug(output_folder_path)
        
        #go back up one
        os.chdir("../")

        for toolchain in toolchains:
            test_command = "mbed test --compile " + " -t " + toolchain + " -m " + target + " " + other_args
            print(module_name + "TEST_COMMAND : " + test_command)
            log.debug(test_command)    
            if args.dontrun == 0:
                try:
                    output = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    output = str(e.output)
                    log.error("COMPILE COMMAND FAILED",toolchain, target)
                log.debug(output)

            test_command = "mbed test --run " + " -t " + toolchain + " -m " + target + " " + other_args + " --report-json " + output_folder_path + "/" + target + "_" + toolchain + "_" + timestamp + "_results.json"
    
            print(module_name + "TEST_COMMAND : " + test_command)
            log.debug(test_command)
            if args.dontrun == 0:
                try:
                    output = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    output = str(e.output)
                    log.error("TEST COMMAND FAILED",toolchain, target)
                log.debug(output)
        if args.scorecard == 1:
            generate_scorecard(output_folder_path, target, mbed_ver, other_args, log)    

def generate_scorecard(output_folder_path, target, mbed_ver, other_args, log) :
#  1. check that all three log files are present, if so, generate the scorecard_data
#       a. get all possible "device_has" data for any targets, use that as the template for all targets,
#          then get "device_has" data for the target, add to scorecard
#        b. read each test log file and add data to the scorecard
#             print any errors
#  2.  validate scorecard and report any errors (create an error.txt file to log errors for each target)

    score_card_file = target + mbed_ver + "_scorecard.json"
    scorecard_data = {}
        
    scorecard_data["date"] = datetime.now().day
    scorecard_data["ver"] = mbed_ver

    for target_entry in TARGETS:
        if target.capitalize() == target_entry.name.capitalize():
            scorecard_data["device_has"] = target_entry.device_has

#get device has data for this target
#Get test data            
    for file in os.listdir(output_folder_path):
        if file.endswith("_results.json"):

            #TODO Need error condition checking such as missing input file, mismatch in target or toolchain, duplicate data, etc.    

             test_data_json_file = os.path.join(output_folder_path, file)    
             log.debug(test_data_json_file)
             #test_data_json_file = "C://Users//maclob01//Documents//Projects//TARGET_PARSING//scorecard_generator/HEXIWEAR_iar_6131936.json"
             
             with open (test_data_json_file, "r") as f:
                test_data = json.loads(f.read()) 
                f.close()
            
                for target_toolchain in test_data:                
                    test_results = {}
                    platform, toolchain = target_toolchain.split("-")
                    #log.debug(platform,toolchain)
                    scorecard_data["name"] = platform
                                    
                    target_test_data = test_data[target_toolchain]
                    for test_suite in target_test_data:
                        test_suite_data = target_test_data[test_suite]  
                        test_results[test_suite] =  test_suite_data.get("single_test_result", "none")
                        
        scorecard_data[toolchain] = test_results    
            
            
    s = json.dumps(scorecard_data)    
    with open (output_folder_path + "//" + target + "_" + mbed_ver + "_scorecard.json", "w") as f:
        f.write(s)
        f.close()


if __name__ == '__main__':
    main()
