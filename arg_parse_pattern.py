import re

# parse pattern
# the order is restricted
# @[gpu=0] command -option ...
# @CMD

# operation
OP_SHOW_JOBS = r"\A[ ]*@(list|l|jobs)"
op_show_jobs = re.compile(OP_SHOW_JOBS)

OP_SHOW_FIN = r"\A[ ]*@(fin|f|finish)"
op_show_fin = re.compile(OP_SHOW_FIN)

OP_DEL_JOB = r"\A[ ]*@del=([0-9][0-9]*)"
op_del_job = re.compile(OP_DEL_JOB)

# options
OPTION = r"\A[ ]*@\[[^\n]*\]"
option = re.compile(OPTION)

OPTION_GPU = r"gpu=([0-9][0-9]*)"
option_gpu = re.compile(OPTION_GPU)

# command
COMMAND = r"[^ \n][^\n]*\Z"
command = re.compile(COMMAND)

# general
NUM = r"([0-9][0-9]*)"
num = re.compile(NUM)