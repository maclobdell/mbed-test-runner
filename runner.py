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
from multiprocessing import Pool
from time import sleep, strftime
from prettytable import PrettyTable

date_format = '%Y-%m-%d %H:%M:%S'

#Warning: Using shell=True can be a security hazard.  Ignoring because I control the command parameters.
#   Used here so I could have the option to pipe output to log file (e.g. command > log.txt).

class ToolException(Exception):
    """A class representing an exception throw by the tools"""
    pass

# Function called by workers
def run_cmd(command, work_dir=None, redirect=False):
    try:
        process = subprocess.Popen(command, bufsize=0, cwd=work_dir)
        _stdout, _stderr = process.communicate()
    except Exception as e:
        print("[OS ERROR] Command: \"%s\" (%s) %s" % (' '.join(command), e.args[0], e.args[1]))
        raise e

    return _stdout, _stderr, process.returncode

# The test worker function that calls the sub-processes. This function cannot accept object classes because it will create an issue with multiprocessing:Pool
def test_worker(job):
    _rc = 255
    results = []
    report_file = None

    for toolchain in job['toolchains']:
        cmd_compile = ["mbed", "test", "--compile", "-t", toolchain, "-m", job['target']] + (job['other_args'].split(' ') if job['other_args'] else [])
        print "EXEC: %s" % ' '.join(cmd_compile)

        if not job['dryrun']:
            try:
                _stdout, _stderr, _rc = run_cmd(cmd_compile)
                results.append({
                    'errno': _rc,
                    'output': _stdout,
                    'command': ' '.join(cmd_compile),
                    'toolchain': toolchain
                })
            except KeyboardInterrupt:
                raise ToolException
            except Exception as e:
                results.append({
                    'errno': e.args[0],
                    'output': e.args[1],
                    'command': ' '.join(cmd_compile),
                    'toolchain': toolchain
                })
                continue

        if not os.path.exists(job['report_dir']):
            os.makedirs(job['report_dir'])

        #Set an appropriate output file name
        if job['report_type'] == "text":
            report_file = job['target'] + "_" + toolchain + "_results.txt"
            report_arg = "--report-text"    
        elif job['report_type'] == "html" :
            report_file = job['target'] + "_" + toolchain + "_results.html"
            report_arg = "--report-html"
        elif job['report_type'] == "xml" :
            report_file = job['target'] + "_" + toolchain + "_results.xml"
            report_arg = "--report-junit"    
        else: #default is to use json output
            report_file = job['target'] + "_" + toolchain + "_results.json"
            report_arg = "--report-json"

        cmd_test = ["mbed", "test", "--run", "-t", toolchain, "-m", job['target'], report_arg, job['report_dir'] + "/" + report_file] + (job['other_args'].split(' ') if job['other_args'] else [])

        if not job['dryrun']:
            try:
                _stdout, _stderr, _rc = run_cmd(cmd_test)
                results.append({
                    'errno': _rc,
                    'output': _stdout,
                    'command': ' '.join(cmd_test),
                    'toolchain': toolchain
                })
            except KeyboardInterrupt:
                raise ToolException
            except Exception as e:
                results.append({
                    'errno': e.args[0],
                    'output': e.args[1],
                    'command': ' '.join(cmd_test),
                    'toolchain': toolchain
                })

    return {
        'errno': _rc,
        'results': results,
        'report_dir': job['report_dir'],
        'report_type': job['report_type'],
        'report_file': report_file
    }

# The test worker function that calls the sub-processes. This function cannot accept object classes because it will create an issue with multiprocessing:Pool
def compile_worker(job):
    _rc = 255
    results = []

    for toolchain in job['toolchains']:
        cmd_compile = ["mbed", "compile", "-t", toolchain, "-m", job['target']] + (job['other_args'].split(' ') if job['other_args'] else [])
        print "EXEC: %s" % ' '.join(cmd_compile)

        if job['dryrun']:
            continue

        try:
            _stdout, _stderr, _rc = run_cmd(cmd_compile)
            results.append({
                'errno': _rc,
                'output': _stdout,
                'command': ' '.join(cmd_compile),
                'toolchain': toolchain
            })
        except KeyboardInterrupt:
            raise ToolException
        except Exception as e:
            results.append({
                'errno': e.args[0],
                'output': e.args[1],
                'command': ' '.join(cmd_compile),
                'toolchain': toolchain
            })
            continue

    return {
        'errno': _rc,
        'results': results,
    }

# The test worker function that calls the sub-processes. This function cannot accept object classes because it will create an issue with multiprocessing:Pool
def custom_worker(job):
    _rc = 255
    results = []

    for toolchain in job['toolchains']:
        cmd_custom = [job['work'], toolchain, job['target']] + (job['other_args'].split(' ') if job['other_args'] else [])
        print "EXEC: %s" % ' '.join(cmd_custom)

        if job['dryrun']:
            continue

        try:
            _stdout, _stderr, _rc = run_cmd(cmd_custom)
            results.append({
                'errno': _rc,
                'output': _stdout,
                'command': ' '.join(cmd_custom),
                'toolchain': toolchain
            })
        except KeyboardInterrupt:
            raise ToolException
        except Exception as e:
            results.append({
                'errno': e.args[0],
                'output': e.args[1],
                'command': ' '.join(cmd_custom),
                'toolchain': toolchain
            })
            continue

    return {
        'errno': _rc,
        'results': results,
    }

workers = {
    'test': test_worker,
    'compile': compile_worker,
    'custom': custom_worker
}


# Work sequentially
def work_seq(work, queue, log):
    worker = workers[work] if work in workers.keys() else workers['custom']

    for item in queue:
        result = worker(item)
        log_result(result, log)
    return True


# Work in parallel
def work_queue(work, queue, jobs_count, log):
    worker = workers[work] if work in workers.keys() else workers['custom']

    p = Pool(processes=jobs_count)
    results = []
    for i in range(len(queue)):
        results.append(p.apply_async(worker, [queue[i]]))
    p.close()

    while len(results):
        sleep(0.1)
        pending = 0
        for r in results:
            if r.ready():
                try:
                    result = r.get()
                    results.remove(r)
                    log_result(result, log)
                except ToolException as err:
                    if p._taskqueue.queue:
                        p._taskqueue.queue.clear()
                        sleep(0.1)
                    p.terminate()
                    p.join()
                    raise Exception(255, "Interrupted by user (Ctrl+C)")
            else:
                pending += 1
                if pending >= jobs_count:
                    break

    results = None
    p.join()

    return True

# Generic logging
def logger(details, log):
    print("%s %s" % (strftime(date_format), details))
    log.info(details)

# Logging of the test result
def log_result(result, log):
    if result['results']:
        for x in result['results']:
            if x['errno']:
                log.error("FAILED: \"%s\" (code: %s)\n%s" % (x['command'], x['errno'], x['output']))
            else:
                log.info("EXEC: \"%s\" (code: %s)\n%s" % (x['command'], x['errno'], x['output']))

    if 'report_type' in result.keys() and result['report_type'] == "json":
        log_test_report(result['report_dir'], result['report_file'], log)

# Logging json
def log_test_report(output_folder_path, report_file, log):
    test_data_json_file = os.path.join(output_folder_path, report_file)
    if not os.path.exists(test_data_json_file):
        logger("JSON FILE MISSING", log)
        return

    with open(test_data_json_file, "r") as f:
        test_data = json.loads(f.read()) 

    #create table
    x = PrettyTable()
    x.field_names = ['target', 'platform_name', 'test suite', 'test case', 'passed', 'failed', 'result', 'time']
    for col in x.field_names:
        x.align[col] = "l"
    x.align[col] = "r"

    #TODO check if file valid, and results are available first

    #read test log for test suite results, put rows in the table
    for target_toolchain in test_data:                
        platform, toolchain = target_toolchain.split("-")
        output_file = platform + "_" + toolchain + "_output.txt"
        target_test_data = test_data[target_toolchain]
        for test_suite in target_test_data:
            test_suite_data = target_test_data[test_suite]
            test_case_data = test_suite_data['testcase_result']
            total_passed = 0
            total_failed = 0
            for test_case in sorted(test_case_data):
                duration = test_case_data[test_case].get('duration', 0.0)
                passed = test_case_data[test_case].get('passed', 0)
                failed = test_case_data[test_case].get('failed', 0)
                result_text = test_case_data[test_case].get('result_text', "UNDEF")
                x.add_row([target_toolchain, platform, test_suite, test_case, passed, failed, result_text, round(duration, 2)])
                total_passed += passed
                total_failed += failed

            x.add_row([target_toolchain, platform, test_suite, "----- TOTAL -----", total_passed, total_failed, test_suite_data.get("single_test_result", "none"), round(float(test_suite_data.get("elapsed_time", 0)), 2)])

            with open(os.path.join(output_folder_path, output_file), "a") as f:
                f.write("\r\nTEST SUITE %s\r\n" % test_suite)
                f.write(re.sub(r'\r\r', '', test_suite_data['single_test_output']))

    logger("TEST RESULTS\r\n%s\r\n" % x, log)


# Logging json
def log_test_summary(output_folder_path, targets, toolchains, log):
    #create table
    x = PrettyTable()
    x.field_names = ["target", "platform_name", "test suite", "result", "time"]
    for col in x.field_names:
        x.align[col] = "l"
    x.align[col] = "r"

    for target in targets:
        for toolchain in toolchains:
            #open the log file
            report_file = target + "_" + toolchain + "_results.json"
            test_data_json_file = os.path.join(output_folder_path, report_file)
            if not os.path.exists(test_data_json_file):
                continue

            with open (test_data_json_file, "r") as f:
                test_data = json.loads(f.read()) 

            #read test log for test suite results, put rows in the table
            for target_toolchain in test_data:                
                platform, toolchain = target_toolchain.split("-")
                target_test_data = test_data[target_toolchain]
                for test_suite in target_test_data:
                    test_suite_data = target_test_data[test_suite]  
                    x.add_row([target_toolchain, platform, test_suite, test_suite_data.get("single_test_result", "none"), round(float(test_suite_data.get("elapsed_time", "none")), 2)])

    logger("TEST RUNNER RESULTS:\r\n%s\r\n" % x, log)

# script arguments
parser = argparse.ArgumentParser(description='Run Mbed OS tests on all connected boards with all toolchains')
parser.add_argument("-t", "--toolchain", default="", action='store', help="Specified toolchain(s). You can provide comma-separated list.")
parser.add_argument("-m", "--mcu", default="", action='store', help="Target icrocontroller")
parser.add_argument("-j", "--jobs", default=1, action='store', help="Number of jobs. Default 1.")
parser.add_argument("-d", "--dryrun", default=False, action='store_true', help="print commands, don't run them")
parser.add_argument("-f", "--folder", default="TEST_OUTPUT", action='store', help="Folder to dump test results to")
parser.add_argument("-r", "--report", default="json", action='store', help="Output format : json, html, text, xml")
parser.add_argument("-o", "--other_args", default="", action='store', help="Other arguments to pass as a string")
parser.add_argument("-w", "--work", default="test", action='store', help="Worker function to call (e.g. test, compile)")

# The main thing
def main():
    args = parser.parse_args()
    other_args = args.other_args
    folder = args.folder  #folder to put the results
    report_type = args.report
    current_path = os.getcwd()
    jobs_count = int(args.jobs)
    work = args.work
    work_title = work.upper()

    if args.toolchain:
        toolchains = args.toolchain.split(",")
    else:
        toolchains = ['GCC_ARM', 'ARM', 'IAR']
    
    if args.mcu:
        muts = [{'platform_name': args.mcu}]
    else:
        #get list of connected boards
        mbeds = mbed_lstools.create()
        muts = mbeds.list_mbeds(filter_function=None, unique_names=True, read_details_txt=False)

    #get timestamp
    dt = datetime.now()
    timestamp =  strftime("%Y-%m-%d %H-%M-%S")

    #Create directory for test results here
    # Output files go in folder structure /<test_output>/<mbed_version>/<platform>
    try:
        os.stat(folder)
    except:
        os.mkdir(folder)
    report_base = folder

    #Set up log
    log_file = current_path + "/" + folder + ("/%s-runner-" % work) + timestamp + ".txt"
    logging.basicConfig(filename=log_file,
        level=logging.DEBUG,
        datefmt=date_format,
        format='[%(asctime)s] %(levelname)s: %(message)s')
    log = logging.getLogger("")
    log.setLevel(logging.DEBUG)     

    logger(" --------------------------------- ", log)
    logger("         %s RUNNER LOG         " % work_title, log)
    logger(" --------------------------------- ", log)
    for mut in muts:
        logger("PLATFORM: " + mut['platform_name'], log)
    for toolchain in toolchains:
        logger("TOOLCHAIN: "  + toolchain, log)
    logger("PATH: " + current_path, log)    
    logger("RESULTS DIR: " + folder, log)
    output = subprocess.check_output("git rev-parse HEAD" , shell=True, stderr=subprocess.STDOUT) #get the branch name
    mbed_ver = re.sub(r'\W+', '', output)  #remove weird characters
    logger("MBED OS HASH: " + mbed_ver, log)

    logger("PARAMETERS: " + other_args, log)
    logger("-----------------------------------", log)

    targets = []
    jobs = []
    for mut in muts:
        target = mut['platform_name']
        targets.append(target)

        job = {
            'work': work,
            'target': target,
            'toolchains': toolchains,
            'timestamp': timestamp,
            'other_args': other_args,
            'report_dir': os.path.join(report_base, mbed_ver, timestamp),
            'report_type': report_type,
            'dryrun': args.dryrun
        }
        jobs.append(job)

    logger("%s STARTED..." % work_title, log)

    if jobs_count <= 1:
        work_seq(work, jobs, log)
    else:
        work_queue(work, jobs, jobs_count, log)
    
    if work == "test":
        log_test_summary(os.path.join(report_base, mbed_ver, timestamp), targets, toolchains, log)

    logger("%s FINISHED" % work_title, log)


if __name__ == '__main__':
    main()
