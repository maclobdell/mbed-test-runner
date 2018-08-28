# simple_mbed_test_runner

This is a simple way to run mbed os tests on several boards.  You kick off a test run, go have coffee or lunch.  When you get back you'll see what tests passed or failed for each connected board for each compiler.  

It is optimized for simplicity, not flexibility or performance.  

Its basically a wrapper around the 'mbed test' command to perform the following functions.
1) run tests on all boards connected to the machine
2) run tests using all compiler toolchain options

Arguments

-o or --other_args, Pass in other arguments such as reference to config files in a string.  See example below.
-d or --dontrun, Don't run the commands, just print them.
-f or --folder, Folder to dump test results to.  By default it will create a folder called "test_output".
-r or --report, Test results output format : json (default), html, text, xml

Running tests
    clone the mbed-os repo you want to tests
    hook up boards to your system (plug in usb cables).
    clone this repo on the same level as the repo you are testing from (mbed-os)
    Execute the following command, passing in arguments (as an example).  

```
    python ../simple_mbed_test_runner/run_all_tests.py  [-o "-n tests-integration-basic -c"] [-d] [-f my_results_folder] [-r html]
```

Output folder structure
    Test result output files go in the following folder structure:

    /[test output folder]/[folder matching the branch name]/[folder for each platform]
    
Logging
    A unique log file in the test results output folder will be generated each time you invoke the script.
    
    log file name: test_runner_log_[timestamp].txt    
    timestamp format: MMDDHHMM
  
    Example Test Log
  
```
INFO:Test Runner:-----------------------------------
INFO:Test Runner:Simple Mbed Test Runner Log
INFO:Test Runner:-----------------------------------
INFO:Test Runner:TIMESTAMP : 8272230
INFO:Test Runner:PLATFORM : MCU54321
INFO:Test Runner:TOOLCHAIN : gcc_arm
INFO:Test Runner:TOOLCHAIN : arm
INFO:Test Runner:TOOLCHAIN : iar
INFO:Test Runner:Path: C:\Users\user01\Documents\mbed-os-5\ci-test-shield
INFO:Test Runner:Results Folder: test_output
INFO:Test Runner:Mbed OS Ver: flexibletests
INFO:Test Runner:Test Parameters: -n tests-* --app-config mbed_app.json
INFO:Test Runner:-----------------------------------
INFO:Test Runner:Testing Started
INFO:Test Runner:Executing Commands...
DEBUG:Test Runner:Results Going To: C:\Users\user01\Documents\mbed-os-5\ci-test-shield\test_output\flexibletests\MCU54321
INFO:Test Runner:mbed test --compile  -t gcc_arm -m MCU54321 -n tests-* --app-config mbed_app.json
DEBUG:Test Runner:Command Output 0
INFO:Test Runner:mbed test --run  -t gcc_arm -m MCU54321 -n tests-* --app-config mbed_app.json --report-json C:\Users\user01\Documents\mbed-os-5\ci-test-shield\test_output\flexibletests\MCU54321/MCU54321_iar_8272230_results.json
ERROR:Test Runner:Result: TEST COMMAND FAILED gcc_arm MCU54321
DEBUG:Test Runner:Command Output None
INFO:Test Runner:+------------------+---------------+-----------------------------+---------+---------------------+
|      target      | platform_name |          test suite         |  result |  elapsed_time (sec) |
+------------------+---------------+-----------------------------+---------+---------------------+
| MCU54321-GCC_ARM |    MCU54321   |    tests-assumptions-spi    |    OK   |    13.0929999352    |
| MCU54321-GCC_ARM |    MCU54321   |    tests-concurrent-comms   |    OK   |     16.135999918    |
| MCU54321-GCC_ARM |    MCU54321   |    tests-api-interruptin    |    OK   |    52.8900001049    |
| MCU54321-GCC_ARM |    MCU54321   |  tests-assumptions-analogin |    OK   |     16.763999939    |
| MCU54321-GCC_ARM |    MCU54321   |      tests-api-analogin     |    OK   |    14.1700000763    |
| MCU54321-GCC_ARM |    MCU54321   |        tests-api-spi        |    OK   |    16.3589999676    |
| MCU54321-GCC_ARM |    MCU54321   |    tests-concurrent-gpio    |    OK   |     42.617000103    |
| MCU54321-GCC_ARM |    MCU54321   |    tests-assumptions-i2c    |    OK   |    12.6129999161    |
| MCU54321-GCC_ARM |    MCU54321   |    tests-concurrent-mixed   |   FAIL  |    18.2970001698    |
| MCU54321-GCC_ARM |    MCU54321   |     tests-api-digitalio     |    OK   |    42.7680001259    |
| MCU54321-GCC_ARM |    MCU54321   | tests-assumptions-digitalio |    OK   |    15.4670000076    |
| MCU54321-GCC_ARM |    MCU54321   |      tests-api-businout     |   FAIL  |    37.6800000668    |
| MCU54321-GCC_ARM |    MCU54321   |        tests-api-i2c        |    OK   |    17.8199999332    |
+------------------+---------------+-----------------------------+---------+---------------------+
INFO:Test Runner:mbed test --compile  -t arm -m MCU54321 -n tests-* --app-config mbed_app.json
DEBUG:Test Runner:Command Output 0
INFO:Test Runner:mbed test --run  -t arm -m MCU54321 -n tests-* --app-config mbed_app.json --report-json C:\Users\user01\Documents\mbed-os-5\ci-test-shield\test_output\flexibletests\MCU54321/MCU54321_iar_8272230_results.json
ERROR:Test Runner:Result: TEST COMMAND FAILED arm MCU54321
DEBUG:Test Runner:Command Output None
INFO:Test Runner:+--------------+---------------+-----------------------------+---------+---------------------+
|    target    | platform_name |          test suite         |  result |  elapsed_time (sec) |
+--------------+---------------+-----------------------------+---------+---------------------+
| MCU54321-ARM |    MCU54321   |    tests-assumptions-spi    |    OK   |    12.9110000134    |
| MCU54321-ARM |    MCU54321   |    tests-concurrent-comms   |    OK   |    15.4409999847    |
| MCU54321-ARM |    MCU54321   |    tests-api-interruptin    |    OK   |    52.6199998856    |
| MCU54321-ARM |    MCU54321   |  tests-assumptions-analogin |    OK   |    16.4320001602    |
| MCU54321-ARM |    MCU54321   |      tests-api-analogin     |    OK   |    13.0779998302    |
| MCU54321-ARM |    MCU54321   |        tests-api-spi        |    OK   |    15.5850000381    |
| MCU54321-ARM |    MCU54321   |    tests-concurrent-gpio    |    OK   |    42.3159999847    |
| MCU54321-ARM |    MCU54321   |    tests-assumptions-i2c    |    OK   |     12.228000164    |
| MCU54321-ARM |    MCU54321   |    tests-concurrent-mixed   |   FAIL  |     17.486000061    |
| MCU54321-ARM |    MCU54321   |     tests-api-digitalio     |    OK   |    42.4689998627    |
| MCU54321-ARM |    MCU54321   | tests-assumptions-digitalio |    OK   |    14.9039998055    |
| MCU54321-ARM |    MCU54321   |      tests-api-businout     |   FAIL  |    37.4170000553    |
| MCU54321-ARM |    MCU54321   |        tests-api-i2c        |    OK   |    17.5910000801    |
+--------------+---------------+-----------------------------+---------+---------------------+

```
