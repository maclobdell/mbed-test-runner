# Mbed Test Runner

This is a simple way to run mbed os tests on several boards.  You kick off a test run, go have coffee or lunch.  When you get back you'll see what tests passed or failed for each connected board for each compiler.  

It is optimized for simplicity, not flexibility or performance.  

Its basically a wrapper around the 'mbed test' command to perform the following functions.
1) run tests on all boards connected to the machine
2) run tests using all compiler toolchain options

## Dependencies
* Mbed OS 5.12 or later
* Mbed CLI 1.10 or later  
* Python 2.7.x or 3.6.x or later

It's a good idea to be familiar with Mbed OS and its tools in order to use this script.

## Arguments

* -o _or_ --other_args
    - Pass in other arguments such as specific tests to run, references to config files, macros, etc.  See example below.
    - For information on all the arguments you can pass in this way, use 'mbed test -h' on your command line.
* -d _or_ --dryrun
    - Don't run the commands, just print them.
* -f _or_ --folder
    - Folder to dump test results to.  By default it will create a folder called "test_output".
* -w _or_ --work
    - Select to compile only or compile & test (default)
* -t _or_ --toolchain
    - The compiler toolchain(s) to run tests with (default is all of these: GCC_ARM, IAR, ARM).  
    - You can provide one or comma-separated list for multiple (-t ARM,GCC_ARM).  
* -m _or_ --mcu
    - The microcontroller to test.  The default is to test all that are connected without having to specify them.  You cannot specify multiple microcontrollers - only a specific one or all (default).

## Running tests
1. Clone the mbed-os repo you want to test
1. Hook up boards to your system (plug in usb cables).
1. Clone this repo on the same level as the repo you are testing from (mbed-os)
1. Execute the following command, passing in arguments (as an example). The path depends on where you have extracted script.


```
    python ../mbed-test-runner/runner.py [-o "-n tests-xyz -c"] [-f my_results_folder]
```

## Output folder structure
Test result output files go in the following folder structure:

/[test output folder]/[timestamp]/

The following files will be generated for each TARGET and TOOLCHAIN combination
* TARGET_TOOLCHAIN_output.txt
* TARGET_TOOLCHAIN_results.html
* TARGET_TOOLCHAIN_results.json
* TARGET_TOOLCHAIN_results.txt
                      
## Logging
A unique log file in the test results output folder will be generated each time you invoke the script.

log file name: test-runner-[timestamp].txt    

Example Test Log from command: 

```
[2019-11-21 10:47:24] INFO:  --------------------------------- 
[2019-11-21 10:47:24] INFO:          TEST RUNNER LOG         
[2019-11-21 10:47:24] INFO:  --------------------------------- 
[2019-11-21 10:47:24] INFO: PLATFORM: MY_TARGET
[2019-11-21 10:47:24] INFO: TOOLCHAIN: IAR
[2019-11-21 10:47:24] INFO: PATH: D:\mbed-os
[2019-11-21 10:47:24] INFO: RESULTS DIR: TEST_OUTPUT
[2019-11-21 10:47:24] INFO: MBED OS HASH: 2e96145b7607de430235dd795ab5350c1d4d64d7
[2019-11-21 10:47:24] INFO: PARAMETERS: 
[2019-11-21 10:47:24] INFO: -----------------------------------
[2019-11-21 10:47:24] INFO: TEST STARTED...
[2019-11-21 12:29:33] INFO: EXEC: "mbed test --compile -t IAR -m MY_TARGET -n tests-mbed_hal-sleep_manager" (code: 0)
[2019-11-21 12:29:34] INFO: TEST RESULTS

+------------------+---------------------------------+-------------------------------------------+--------+--------+---------+--------+
| target/toolchain | test suite                      | test case                                 | passed | failed | result  |   time |
+------------------+---------------------------------+-------------------------------------------+--------+--------+---------+--------+
| MY_TARGET-IAR     | tests-mbed_hal-sleep_manager   | deep sleep lock/unlock                    | 1      | 0      | OK      |   0.04 |
+------------------+---------------------------------+-------------------------------------------+--------+--------+---------+--------+


[2019-11-21 12:29:34] INFO: TEST SUMMARY PER TARGET-TOOLCHAIN:

+------------------+------------------------------------------------------------------------------+---------+--------+
| target/toolchain | test suite                                                                   | result  |   time |
+------------------+------------------------------------------------------------------------------+---------+--------+
| MY_TARGET-IAR    | tests-mbed_hal-sleep_manager                                                 | OK      |  18.75 |
+------------------+------------------------------------------------------------------------------+---------+--------+


[2019-11-21 12:29:34] INFO: TEST SUMMARY PER TARGET:

+----------+------------------------------------------------------------------------------+---------+--------+
| target   | test suite                                                                   | result  |   time |
+----------+------------------------------------------------------------------------------+---------+--------+
| MY_TARGET | tests-mbed_hal-sleep_manager                                                | OK      |  18.75 |
+----------+------------------------------------------------------------------------------+---------+--------+

[2019-11-21 12:29:34] INFO: TEST FINISHED

```

## Usage Tips
On Linux, you can create an alias to shorten the command.  Just reference the path to the script.

```
    alias runner="python /home/mbed-test-runner/runner.py"
```

On Windows, you create a similar command alias by creating a batch file called *runner.bat* with the following contents.  Then add the path to the batch file to your PATH environment variable.  This also depends on where you installed the script.

```
python C:\Users\my_username\Documents\mbed-test-runner\runner.py %*
```

Then run the script from anywhere by typing this on a command line.  
```    
    runner [arguments]
```    
