:; # This is perfectly cross-platform, only the comments will run on linux. Just has to eb a bat so windows recognizes it as a script.
:; python3 test_args.py "$@" && ./run.sh "$@"
:; exit
python main.py -n %*
