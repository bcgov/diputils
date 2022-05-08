# 20190711
#echo setting up environment..
#source bash_profile

echo compiling multicore compiler..
python setup.py multicore; ./compile_jobs.sh

echo compile whitespace remover..
python setup.py ws; ./compile_jobs.sh

echo compiling c/c++ simple autoformatter..
python setup.py dent; ./compile_jobs.sh

echo run setup.py..
/cygdrive/c/Program\ Files/Python35/python.exe setup.py > /dev/null

echo cleaning code..
multicore clean_jobs.sh

echo compile utilities..
multicore compile_jobs.sh

echo setting permissions..
icacls  .   /grant everyone:F  /t > /dev/null

echo done
