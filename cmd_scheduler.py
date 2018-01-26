import os
import time
from datetime import datetime

from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing import Manager

import subprocess
from subprocess import Popen

import argparse
import re

import arg_parse_pattern

_CLOCK = 5 # sec

# well, it might be redundant...
class SchedulerConfig:
	def __init__(self, args=None):
		# default setting
		if args is None:
			self.gpus = 1
			self.file_extension = ".txt"
			self.save_dir = os.path.expanduser("~/gpu_dispatch_results")

		else:
			self.gpus = args.gpus
			self.file_extension = args.file_extension
			self.save_dir = os.path.expanduser(args.save_dir)

class _SubProcess:
	def __init__(self, subproc, parent_pipe):
		self.process = subproc
		self.pipe = parent_pipe

class _SchedulerJobs:
	def __init__(self, cmd, job_num, gpu_num, status=0, save_name="log", time_stamp=True):
		self.cmd = cmd
		self.job_num = job_num
		self.gpu_num = gpu_num
		self.status = status
		self.save_name = save_name
		self.time_stamp = time_stamp

class Scheduler:
	def __init__(self, config=None):
		# default setting
		if config is None:
			self.config = SchedulerConfig()
		else:
			self.config = config

		self.job_queue = []
		self.subproc_list = []
		self.job_number = 0;
		self.recv_cmd_file = None
		self.fin_cmd_file = None
		self.manager = None

		# setup setting to schedule jobs
		self._init_scheduler()

	def __del__(self):
		if self.recv_cmd_file is not None:
			self.recv_cmd_file.close()

		if self.fin_cmd_file is not None:
			self.fin_cmd_file.close()

		if self.manager is not None:
			self.manager.shutdown()

	def _init_scheduler(self):
		for i in range(self.config.gpus):
			parent_pipe, child_pipe = Pipe()
			self.subproc_list.append(_SubProcess(Process(target=self._run_subproc, args=(i, child_pipe, )), parent_pipe))
			self.subproc_list[-1].process.start()

		if os.path.exists(self.config.save_dir) == False:
			os.mkdir(self.config.save_dir)
			print("made path {}".format(self.config.save_dir))

		# file name for saving received command.
		self.file_name = "{}.txt".format(datetime.now().strftime('%b%d_%H-%M-%S'))

		self.manager = Manager()
		self.job_queue = self.manager.list()

		self.dispatcher = Process(target=self._dispatch, args=())
		self.dispatcher.start()

		self.recv_cmd_file = open("{}".format(os.path.join(self.config.save_dir, "recv_cmd_"+self.file_name)), "w")

	def _del_job(self, del_num):
		if del_num <= self.job_number:
			for que_idx, job in enumerate(self.job_queue):
				if del_num == job.job_num:
					self.job_queue.pop(que_idx)
					return True

		return False

	def _return_op_message(self, msg=""):
		return _SchedulerJobs(msg, -1, 99999, -1)

	def _validate(self, cmd):
		def _return_message(msg=""):
			return _SchedulerJobs(msg, -1, 99999, -1)
		
		# check is there @list or @jobs
		match_pattern = arg_parse_pattern.op_show_jobs.search(cmd)
		if match_pattern is not None:
			print("############################")
			print("que. : in queue number\nNo. : job number, order of push\ngpu : -1 means don't care")
			print("que. : No.  | gpu | command")
			for idx, job in enumerate(self.job_queue):
				print("{:4} : {:5}|{:5}| {}".format(idx, job.job_num, job.gpu_num, job.cmd))
			return _return_message("")

		# check is there @del=%d
		match_pattern = arg_parse_pattern.op_del_job.search(cmd)
		if match_pattern is not None:
			del_num = arg_parse_pattern.num.search(match_pattern.group())
			if del_num is not None:
				if self._del_job(int(del_num.group())):
					return _return_message("delete success.")
				else:
					return _return_message("cannot delete.")
			else:
				return _return_message("@del=NUMBER please.")

		# init
		gpu_num = -1

		# check the options
		match_pattern = arg_parse_pattern.option.search(cmd)
		if match_pattern is not None:
			# check for gpu option
			gpu_option = arg_parse_pattern.option_gpu.search(match_pattern.group())
			if gpu_option is not None:
				gpu_num = arg_parse_pattern.num.search(gpu_option.group())
				if gpu_num is not None:
					gpu_num = int(gpu_num.group())
					if gpu_num > self.config.gpus:
						return _return_message("cannot assign that # for GPU.")
				else:
					return _return_message("gpu=NUMBER please.")
			else:
				gpu_num = -1

		# check is there a command
		match_pattern = arg_parse_pattern.command.search(cmd)
		if match_pattern is not None:
			cmd_str = match_pattern.group()
		else:
			return _return_message("")

		new_job = _SchedulerJobs(cmd_str, self.job_number, gpu_num, 0)
		#return _SchedulerJobs(cmd, self.job_numbers, pars.gpu_num, pars.job_status, pars.save_name, pars.time_stamp)
		self.job_number += 1

		return new_job

	def _wait_input(self):
		while True:
			command = input(">")
			pars = self._validate(command)
			if pars.status < 0:
				if len(pars.cmd) > 0:
					print(pars.cmd)
				continue

			self.job_queue.append(pars)
			self.recv_cmd_file.write("{}\n".format(pars.cmd))
			self.recv_cmd_file.flush()
			print("pushed to job queue.")

	def _dispatch(self):
		dispatched_jobs = [ None for i in range(len(self.subproc_list))]
		with open("{}".format(os.path.join(self.config.save_dir, "fin_cmd_"+self.file_name)), "w") as fin_cmd_file:
			while True:
				for id_num, sp in enumerate(self.subproc_list):
					if sp.pipe.poll():
						if dispatched_jobs[id_num] is not None:
							fin_cmd_file.write("{}\n".format(dispatched_jobs[id_num].cmd))
							fin_cmd_file.flush()
							dispatched_jobs[id_num] = None

						for job_queue_num, job in enumerate(self.job_queue):
							if job.gpu_num == id_num or job.gpu_num < 0:
								_ = sp.pipe.recv()
								sp.pipe.send(job)
								dispatched_jobs[id_num] = job
								self.job_queue.pop(job_queue_num)
								break;
				
				time.sleep(_CLOCK)

	def _run_subproc(self, id_num, child_pipe):
		"""
			it is not thought to be stop in the middle of calculating.
		"""
		while True:
			child_pipe.send("ready")
			# fetch job
			job = child_pipe.recv()
			# checj job status for halting.
			if job.status < 0:
				break;
			if id_num != job.gpu_num and job.gpu_num >= 0:
				print("dispatch error... skipping.")
				continue

			# get time of now.
			time_stamp = datetime.now().strftime('%b%d_%H-%M-%S')

			# making path of log file to save log. 
			save_path = os.path.join(self.config.save_dir, "{}_{}{}{}".format(job.job_num, time_stamp+"_" if job.time_stamp else "", job.save_name, self.config.file_extension))
			
			try:
				# run command and write out to log file.
				#subprocess.call("{} > {}".format(job.cmd, save_path), shell=True)
				
				# in the case of using tqdm, "\r" does not work on writing in file, so we delete it...
				proc = Popen( "{} > {}".format(job.cmd, save_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				proc.wait()

			except Exception as e:
				# skip error for keep the sytle.
				"""
				import traceback
				traceback.print_exc()
				print(e)
				"""
				pass

			#res = commands.getoutput("{} > {}".format(job.cmd, save_path))

	def start(self):
		self._wait_input()




if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('--save_dir', type=str, default='gpu_dispatch_results', help='directory of save logs.')
	parser.add_argument('--file_extension', type=str, default='.txt', help='extension of log file.')
	parser.add_argument('--gpus', type=int, default=1, help='Scheduling for how many GPUs.')
	
	# not yet, is this even possible?
	#parser.add_argument('-tmux', action="store_true", default=False, help='use tmux along training.')

	args = parser.parse_args()

	config = SchedulerConfig(args)
	scheduler = Scheduler(config)
	scheduler.start()

