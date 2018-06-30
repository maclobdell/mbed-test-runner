#!/usr/bin/env python
import argparse
import os.path
import subprocess
import datetime
from datetime import datetime
import sys
import json
from os.path import join, abspath, dirname
from json import load, dump
import re

#this script must run in a mbed-os top level directory
ROOT = "."
sys.path.insert(0, ROOT)
from tools.targets import TARGETS

parser = argparse.ArgumentParser(description='Generate Scorecards')
parser.add_argument("-d", "--dontrun", default=0, action='count', help="print commands, don't run them")  #just check if present
parser.add_argument("-f", "--folder", default="test_output", action='store', help="Folder to find test results")  #default is string

def main():
    module_name = "[generate_scorecards.py] : "
    
    args = parser.parse_args()

    folder = args.folder

# files go in folder structure /<test_output>/<mbed_version>/<platform>

    #change to the test results directory
    try:
        os.chdir(folder)
    except:
        print "expected test results folder does not exist"

    #identify sub directores that hold results for various mbed os versions
    for v in os.listdir("."):
        if os.path.isdir(v):
            mbed_ver = v
            print "mbed os ver:", v
            os.chdir(v)
                #identify sub directores that hold results for various platforms
            for t in os.listdir("."):
                if os.path.isdir(t):
                    target = t
                    print "target:", t
                    os.chdir(t)    
                    if args.dontrun == 0:
                        generate_scorecard("./", target, mbed_ver)    
                    os.chdir("../")        
def generate_scorecard(output_folder_path, target, mbed_ver) :
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
             #print test_data_json_file
             #test_data_json_file = "C://Users//maclob01//Documents//Projects//TARGET_PARSING//scorecard_generator/HEXIWEAR_iar_6131936.json"
             
             with open (test_data_json_file, "r") as f:
                test_data = json.loads(f.read()) 
                f.close()
            
                for target_toolchain in test_data:                
                    test_results = {}
                    platform, toolchain = target_toolchain.split("-")
                    #print platform,toolchain
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
