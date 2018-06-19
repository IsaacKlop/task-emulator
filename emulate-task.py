import argparse
import threading
import subprocess
import consul
from time import sleep

parser = argparse.ArgumentParser(description="Container that uses stress and iPerf3 to emulate a task")
parser.add_argument("-c", "--cpu", help="number of CPU workers")
parser.add_argument("-m", "--memory", help="allocate memory (in MB)")
parser.add_argument("-t", "--timeout", help="time to run (in seconds)", default=10)
parser.add_argument("-b", "--bandwidth", help="network traffic (in Mb/s)")
parser.add_argument("--host", help="target host for iperf3", default="127.0.0.1")
parser.add_argument("-p", "--port", help="target host port", default=5201)
parser.add_argument("-i", "--id", help="task ID", required=True)
args = parser.parse_args()

def stress_cpu(cpu,timeout):
  # Start CPU cycles
  command = ("/usr/bin/stress", "-c", str(cpu), "-t", str(timeout))
  popen = subprocess.Popen(command, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  print(output)

def stress_memory(memory,timeout):
  # Allocate memory
  command = ("/usr/bin/stress", "-m", "1", "--vm-bytes", str(memory)+"M", "-t", str(timeout))
  popen = subprocess.Popen(command, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  print(output)

def iperf_client(host,port,bandwidth,timeout):
  # Send network traffic to an iPerf server
  command = ("/usr/bin/iperf3", "-c", str(host), "-p", str(port), "-b", str(bandwidth)+"M", "-t", str(timeout))
  popen = subprocess.Popen(command, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  print(output)

def iperf_server(port):
  # Start an iPerf server which terminates after one connection
  command = ("/usr/bin/iperf3", "-s", "-p", str(port), "-1")
  popen = subprocess.Popen(command)
  popen.wait()

def finish_task():
  # Write value to Consul to signal end of task
  task_id = args.id
  c = consul.Consul(host="145.100.104.102")
  print(task_id)
  c.kv.put(task_id, '1')

# Initalize threads
class myThread (threading.Thread):
  def __init__(self, threadID):
    threading.Thread.__init__(self)
    self.threadID = threadID
  def run(self):
    if (self.threadID == 1):
      iperf_server(args.port)
    elif (self.threadID == 2):
      stress_cpu(args.cpu,args.timeout)
    elif (self.threadID == 3):
      stress_memory(args.memory,args.timeout)
    elif (self.threadID == 4):
      iperf_client(args.host,args.port,args.bandwidth,args.timeout)

thread1 = myThread(1)
thread2 = myThread(2)
thread3 = myThread(3)
thread4 = myThread(4)

# Start relevant threads
# Join threads and wait for all of them to finish before writing to Consul
if (args.bandwidth):
  # Start a local server if the target host is this container
  if ((args.host == "127.0.0.1") or (args.host == "localhost")):
    thread1.start()
    thread1.join()
    # Allow server to start up before calling client
    sleep(1)
  thread4.start()
  thread4.join()

if (args.cpu):
  thread2.start()
  thread2.join()

if (args.memory):
  thread3.start()
  thread3.join()

finish_task()
