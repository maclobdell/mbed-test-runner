#!/usr/bin/env python
import argparse
import os.path
import subprocess
import datetime
from datetime import datetime
import mbed_lstools

parser = argparse.ArgumentParser(description='Run Mbed OS tests for all toolchains')
parser.add_argument("-m", type=str, default=["auto"], action='append', help="Target Name")

#Warning: Using shell=True can be a security hazard.  Ignoring because I control the command parameters.
#   Used here so I can pipe output to log file using in shell command verses piping the output it with python.

def main():

    module_name = "[run_all_tests.py] : "
    #other_args = "-n tests-* --app-config .\mbed_app.json"  #for CI Test Shield
    #other_args = "-n tests-mbed_hal-sleep* -c"
    other_args = ""

    toolchains = ['gcc_arm', 'arm', 'iar']
    #toolchains = ['gcc_arm']

    args = parser.parse_args()
    ## TODO: Get argument parsing working.

    mbeds = mbed_lstools.create()
    muts = mbeds.list_mbeds(filter_function=None, unique_names=True, read_details_txt=False)

    hr = datetime.now().hour
    min = datetime.now().minute
    sec = datetime.now().second
    timestamp =  str(hr) + str(min) + str(sec)

    print(module_name + "TIMESTAMP : " + timestamp)

    for mut in muts:
        print(module_name + "FOUND : " + mut['platform_name'])
    for toolchain in toolchains:
        print(module_name + "TOOLCHAIN : "  + toolchain)

    for mut in muts:
        target = mut['platform_name']

        for toolchain in toolchains:
            test_command = "sudo mbed test --compile " + " -t " + toolchain + " -m " + target + " " + other_args
            print(module_name + "TEST_COMMAND : " + test_command)
            try:
                output = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
            except Exception, e:
                output = str(e.output)
            print output

            test_command = "sudo mbed test --run " + " -t " + toolchain + " -m " + target + " " + other_args + " --report-html " + target + "_" + toolchain + "_" + timestamp + ".html"
            print(module_name + "TEST_COMMAND : " + test_command)
            try:
                output = subprocess.check_call(test_command , shell=True, stderr=subprocess.STDOUT)
            except Exception, e:
                output = str(e.output)
            print output

if __name__ == '__main__':
    main()
