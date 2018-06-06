#!/usr/bin/env python
import argparse
import os.path
import subprocess
import datetime
from datetime import datetime
import mbed_lstools

parser = argparse.ArgumentParser(description='Run Mbed OS tests on all connected boards with all toolchains')
parser.add_argument("-o", "--other_args", default="", action='store', help="Other arguments to pass as a string")  #default is string
parser.add_argument("-d", "--dontrun", default=0, action='count', help="print commands, don't run them")  #just check if present
parser.add_argument("-f", "--folder", default="test_output", action='store', help="Folder to dump test results to")  #default is string

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

    #create directory for output folder here
    try:
        os.stat(folder)
    except:
        os.mkdir(folder)

    for mut in muts:
        target = mut['platform_name']

        for toolchain in toolchains:
            test_command = "mbed test --compile " + " -t " + toolchain + " -m " + target + " " + other_args
            print(module_name + "TEST_COMMAND : " + test_command)

            if args.dontrun == 0:
                try:
                    output = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    output = str(e.output)
                print output

            test_command = "mbed test --run " + " -t " + toolchain + " -m " + target + " " + other_args + " --report-html " + "./" + folder + "/" + target + "_" + toolchain + "_" + timestamp + ".html"
            print(module_name + "TEST_COMMAND : " + test_command)

            if args.dontrun == 0:
                try:
                    output = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    output = str(e.output)
                print output

if __name__ == '__main__':
    main()
