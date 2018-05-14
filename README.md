# simple_mbed_test_runner

This is a simple way to run mbed os tests on several boards.  You kick off a test run, go have coffee or lunch.  When you get back you'll see what tests passed or failed for each connected board for each compiler.  

It is optimized for simplicity, not flexibility or performance.  

Its basically a wrapper around the 'mbed test' command to perform the following functions.
1) run tests on all boards connected to the machine
2) run tests using all compiler toolchain options

Future Arguments
(These aren't implemented yet)
-b --branch (branch to checkout)
-e --exclude (exclude board or toolchain)
-n --name (pass in names of tests to run, default is all)
-o --other_args (pass in other arguments such as reference to config files)

Running tests
    clone the mbed-os repo you want to tests
    hook up boards to your system (plug in usb cables).
    clone this repo on the same level as the repo you are testing from (mbed-os)
    Execute the following command.  
```
    python ../simple_mbed_test_runner/run_all_tests.py
```

Known Issues
- argument passing is not working yet (features not implemented)
- the script currently inserts 'sudo' to run commands on linux to avoid permissions issues.  This is obviously not ideal and won't work on Windows.
- running this tool is not ideal.  In the future I'll recommend a different procedure.   
