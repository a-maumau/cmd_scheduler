# Usage  
```
python cmd_scheduler.py
```  
  
# Commands  
if you run the script, you can use some commands to control the queue  
  
@list        : shows the list of job in queue.  
@del=job_num : delete the job witch has a job number of "job_num"  
  
example:  
```
> @list
############################
que. : queue number.
No.  : job number in pushed order.
gpu  : -1 means don't care what # of gpu to use.
que. : No.  | gpu | command
   0 :     1|    1| @[gpu=1] python test_sleep.py
   1 :     2|    0| @[gpu=0] python test_sleep.py
   2 :     3|    0| @[gpu=0] python test_sleep.py
```

# Parameter  
order of "@[parameters] command" should be kept  
  
gpu=num  : use gpu that is assigned "num" in the system  
  
example:  
```
> @[gpu=0] python test_sleep.py
```
