# Note
**THIS PROGRAM IS NOT SCHEDULING WITH GPU NUMBER.**  
only associate with which gpu are you going to use.  
So if you use the parameter of "gpu=#", you need to set the same number in the code.  
  
if you use "gpu=#", you need set assign gpu number.  
pytorch :  
`.cuda(#NUMBER)` or `with torch.cuda.device(#NUMBER):`  

# Usage
```
python cmd_scheduler.py
```  
  
# Commands  
if you run this script, you can use some commands to control the queue  
  
@list        : shows the list of job in queue.  
@fin         : shows the list of finished jobs.
@del=job_num : delete the job witch has a job number of "job_num".  
  
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
