:; # This is perfectly cross-platform, only the comments will run on linux. Just has to eb a bat so windows recognizes it as a script.
:; python3 test_args.py "$@" && ./run.sh "$@"
:; exit

set exectutable = ""

where /q py
IF ERRORLEVEL 1 (
    where /q python
    IF ERRORLEVEL 1 (
        ECHO Please install python 3.9 or higher.
        EXIT /B
    ) ELSE (
       set executable = python
    )
) ELSE (
    set executable = py
)

%executable% test_for_windows_libs.py
%executable% main.py -n %*
