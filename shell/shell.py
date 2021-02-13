#! /usr/bin/env python3

import os, sys, re

while 1:
  os.write(1, '$ '.encode())
  input = os.read(0, 1000)

  if input.decode('utf-8')[0:4] == 'exit':
    os.write(1, 'Goodbye!\n'.encode())
    sys.exit(0)

  rc = os.fork()

  if rc < 0:
    os.write(2, 'Fork failed!\n'.encode())
    sys.exit(0)
  elif rc == 0:
    # Do the prcess of the passed input parameters
    # os.write(1, 'Child!\n'.encode())
    
    args = re.split(' ', input.decode('utf-8')[0:-1])
    for dir in re.split(":", os.environ['PATH']):
      program = "%s/%s" % (dir, args[0])
      # os.write(1, 'Trying to execute...\n'.encode())
      try:
        os.execve(program, args, os.environ)
      except FileNotFoundError:
        pass
      
    os.write(2, ('Could not find \'%s\' program to execute'%args[0]).encode())
    sys.exit(1)


  else:
    os.wait()
    # os.write(1, 'Parent!\n'.encode())
  # os.write(1, input)
