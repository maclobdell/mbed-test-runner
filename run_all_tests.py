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
from prettytable import PrettyTable

parser = argparse.ArgumentParser(description='Run Mbed OS tests on all connected boards with all toolchains')
parser.add_argument("-o", "--other_args", default="", action='store', help="Other arguments to pass as a string")  #default is string
parser.add_argument("-d", "--dontrun", default=0, action='count', help="print commands, don't run them")  #just check if present
parser.add_argument("-f", "--folder", default="test_output", action='store', help="Folder to dump test results to")  #default is string
parser.add_argument("-r", "--report", default="json", action='store', help="Output format : json, html, text, xml")  #default is string

#Warning: Using shell=True can be a security hazard.  Ignoring because I control the command parameters.
#   Used here so I could have the option to pipe output to log file (e.g. command > log.txt).


def main():

    args = parser.parse_args()

    other_args = args.other_args
    folder = args.folder  #folder to put the results
    report_type = args.report

    current_path = os.getcwd()

    toolchains = ['gcc_arm', 'arm', 'iar']

    #get list of connected boards
    mbeds = mbed_lstools.create()
    muts = mbeds.list_mbeds(filter_function=None, unique_names=True, read_details_txt=False)

    #get timestamp
    mo = datetime.now().month
    day = datetime.now().day
    hr = datetime.now().hour
    min = datetime.now().minute
    timestamp =  str(mo) + str(day) + str(hr) + str(min)

    #Create directory for test results here
    # Output files go in folder structure /<test_output>/<mbed_version>/<platform>
    try:
        os.stat(folder)
    except:
        os.mkdir(folder)

    #Set up log
    log_file_path = current_path + "/" + folder + "/test_runner_log_" + timestamp + ".txt"
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

    logger("Path: " + current_path,log)    
    logger("Results Folder: " + folder,log)
    
    #get the branch name
    output = subprocess.check_output("git rev-parse --abbrev-ref HEAD" , shell=True, stderr=subprocess.STDOUT)    
    
    mbed_ver = re.sub(r'\W+', '', output)  #remove weird characters
    logger("Mbed OS Ver: " + mbed_ver,log)

    logger("Test Parameters: " + other_args,log)
    logger("-----------------------------------",log)
    
    #change to the test results output directory
    os.chdir(folder)

    #create directory for the mbed version results - this is just the branch name (or maybe tag?)
    try:
        os.stat(mbed_ver)
    except:
        os.mkdir(mbed_ver)

    #change to the directory that is named the same as the mbed os version  / branch or tag name
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
        
        #The output folder path is the name of the directory at /<test_output>/<mbed_version>/<platform>
        output_folder_path = os.getcwd()
        log.debug("Results Going To: " + output_folder_path)
        
        #Go back up one
        os.chdir("../")

        #Set an appropriate output file name
        if report_type == "text":
            output_file_name = target + "_" + toolchain + "_" + timestamp + "_results.txt"
            report_arg = "--report-text"    
        elif report_type == "html" :
            output_file_name = target + "_" + toolchain + "_" + timestamp + "_results.html"
            report_arg = "--report-html"
        elif report_type == "xml" :
            output_file_name = target + "_" + toolchain + "_" + timestamp + "_results.xml"
            report_arg = "--report-junit"    
        else:
            #anytthing else, use json output
            output_file_name = target + "_" + toolchain + "_" + timestamp + "_results.json"
            report_arg = "--report-json"
        
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
            
            test_command = "mbed test --run " + " -t " + toolchain + " -m " + target + " " + other_args + " " + report_arg + " " + output_folder_path + "/" + output_file_name    
            logger(test_command,log)
            
            if args.dontrun == 0:
                try:
                    call_result = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    call_result = str(e.output)
                    log.error("Result: TEST COMMAND FAILED " + toolchain + " " + target)
                log.debug("Command Output " + str(call_result))

                if report_type == "json":
                    log_test_summary(output_folder_path, output_file_name, log)
                            
                 
def logger(details, log):
    print(details)
    log.info(details)
    
def log_test_summary(output_foler_path, output_file_name, log):    
        #open the log file 
        test_data_json_file = os.path.join(output_foler_path, output_file_name)    
        with open (test_data_json_file, "r") as f:
            test_data = json.loads(f.read()) 
            f.close()

        #create table
        x = PrettyTable()        
        x.field_names = ["target", "platform_name", "test suite", "result"," elapsed_time (sec)"]

        #TODO check if file valid, and results are available first

        #read test log for test suite results, put rows in the table
        for target_toolchain in test_data:                
            platform, toolchain = target_toolchain.split("-")
            target_test_data = test_data[target_toolchain]
            for test_suite in target_test_data:
                test_suite_data = target_test_data[test_suite]  
                x.add_row([target_toolchain, platform, test_suite, test_suite_data.get("single_test_result", "none"),test_suite_data.get("elapsed_time", "none")])

        logger(x, log)

if __name__ == '__main__':
    main()
