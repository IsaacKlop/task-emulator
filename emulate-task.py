import argparse
import threading
import subprocess
from time import sleep

parser = argparse.ArgumentParser(description="Container that uses stress and iPerf3 to emulate a task")
parser.add_argument("-c", "--cpu", help="number of workers", default=1)
parser.add_argument("-m", "--memory", help="allocate memory (MB)", default=256)
parser.add_argument("-t", "--timeout", help="time to run", default=10)
parser.add_argument("-b", "--bandwidth", help="network traffic in Mb/s")
parser.add_argument("--host", help="target host for iperf3", default="127.0.0.1")
parser.add_argument("-p", "--port", help="target host port", default=5201)
args = parser.parse_args()

def stress(cpu,memory,timeout):
  command = ("/usr/bin/stress", "-c", str(cpu), "-m", "1", "--vm-bytes", str(memory)+"M", "-t", str(timeout))
  popen = subprocess.Popen(command, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  print(output)

def iperf_client(host,port,bandwidth,timeout):
  command = ("/usr/bin/iperf3", "-c", str(host), "-p", str(port), "-b", str(bandwidth)+"M", "-t", str(timeout))
  popen = subprocess.Popen(command, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  print(output)

def iperf_server(port):
  command = ("/usr/bin/iperf3", "-s", "-p", str(port), "-1")
  popen = subprocess.Popen(command)
  popen.wait()

class myThread (threading.Thread):
  def __init__(self, threadID):
    threading.Thread.__init__(self)
    self.threadID = threadID
  def run(self):
    if (self.threadID == 1):
      iperf_server(args.port)
    elif (self.threadID == 2):
      stress(args.cpu,args.memory,args.timeout)
    elif (self.threadID == 3):
      iperf_client(args.host,args.port,args.bandwidth,args.timeout)

thread1 = myThread(1)
thread2 = myThread(2)
thread3 = myThread(3)

if (args.bandwidth):
  # Start a local server if the target host is this container
  if ((args.host == "127.0.0.1") or (args.host == "localhost")):
    thread1.start()
    # Allow server to start up before calling client
    sleep(1)
  thread3.start()

thread2.start()
