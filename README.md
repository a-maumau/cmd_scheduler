# Usage  
```
python cmd_scheduler.py
```  
  
# Commands  
if you run the script, you can use some commands to control the queue  
  
@list        : shows the list of pushed in queue.
@del=job_num : delete the job witch has a job number "job_num"
  
example:  
```
> @list
############################
que. : in queue number
No. : job number, order of push
gpu : -1 means don't care
que. : No.  | gpu | command
   0 :     1|    1| @[gpu=1] python test_sleep.py
   1 :     2|    0| @[gpu=0] python test_sleep.py
   2 :     3|    0| @[gpu=0] python test_sleep.py
```

# Parameter  
order of "@[parameters] command" should be kept  
  
gpu=num  : use gpu # "num"  
  
example:  
```
> @[gpu=0] python test_sleep.py
```
