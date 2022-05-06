#  Copyright 2019 Province of British Columbia
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

'''20190212 multicore.py run (terminal) batch jobs using multiple cores..

20190601 tested: added flag to optionally start one process right away for every job!'''
import os
import sys
import time
from misc import *
import multiprocessing
from thread import allocate_lock, start_new_thread

args = sys.argv
if len(args) < 2:
    err('multicore.py:\n' +
        'usage: multicore [text file: one sys cmd per line] # init one thread per cpu\n' +
        'multicore [text file: one syscmd per line] 1 # init one thread per job')
one_worker_per_job, n_workers = False, None
if len(args) > 2:
    one_worker_per_job = True if sys.argv[2] == "1" else False
    # see if a different number of workers was specified
    try:
        if int(sys.argv[2]) > 1:
            n_workers = int(sys.argv[2])
    except:
        pass

fn, ncpu = args[1], multiprocessing.cpu_count()
if not os.path.exists(fn):
    err('job file: ' + fn.strip() + ' not found')
task = open(fn).read().strip().split("\n")
tasks, n_task = [x.strip() for x in task], len(task)

# default is to set up a work queue and have as many workers as cpus, picking up tasks..
#..alternately, can set up one worker per job
if one_worker_per_job:
    ncpu = n_task
else:
    if n_workers and n_workers > 1:
        ncpu = n_workers

# concurrency control
lock, p_lock = allocate_lock(), allocate_lock()
threads_alive, next_j, j_max = ncpu, 0, n_task - 1

# printf with lock
def cprint(s):
    global p_lock
    p_lock.acquire(); print s; p_lock.release()

ncpu *= 1
cprint("nworker: " + str(ncpu))
#worker thread takes a task from the list
def threadfun(my_id):
    global next_j, j_max, lock, threads_alive, tasks
    job_times = []
    while True:  # acquire lock, fetch task index
        lock.acquire()
        j, next_j = next_j, next_j + 1
        lock.release()  # kill off thread if no more work
	if(j > j_max):
	    threads_alive -= 1
	    return

        if tasks[j].strip() == "":
            continue  # don't run empty task

        # run task, divide into subtask
        work = tasks[j].split(";")  # run task
        for i in range(0, len(work)): 
            cprint("worker(" + str(my_id) + "): " + work[i])
            os.popen(work[i]).read()
            cprint("\tworker(" + str(my_id) + ")")

# sleep while task being processed
def wait_to_finish():
    poll_int = .05 # polling is bad, don't do too much
    while True:
        time.sleep(poll_int)
	if(threads_alive == 0): sys.exit(0)

for i in range(0, ncpu):
    start_new_thread(threadfun, (i, ))
wait_to_finish()
