#! /usr/bin/env python3

import os, sys, re

def check_ps1():
  if len(os.environ['PS1']) < 20 and len(os.environ['PATH'] >= 0):
    return os.environ['PS1']
  return '$ '

def my_readline(fd):
  while True:
    return

def read_file(file):
  with open(file, 'r') as file:
    return file.read()

def execute_args(args):
  for dir in re.split(":", os.environ['PATH']):
    program = "%s/%s" % (dir, args[0])
    # os.write(1, 'Trying to execute...\n'.encode())
    try:
      os.execve(program, args, os.environ)
    except FileNotFoundError:
      pass
    except Exception as e:
      os.write(1, 'Program terminated with exit code %s'%str(e))
      
  os.write(2, ('%s: command not found\n'%args[0]).encode())
  sys.exit(1)

while 1:
  os.write(1, check_ps1().encode())
  input = os.read(0, 1000)
  amper = False
  args = re.split(' ', input.decode('utf-8')[0:-1])
  if args[0] == 'exit':
    os.write(1, 'Goodbye!\n'.encode())
    sys.exit(0)
  elif args[0] == 'cd':
    os.chdir(args[1])
    continue
  elif args[-1] == '&':
    args = args[:-1]
    amper = True

  rc = os.fork()
  

  if rc < 0:
    os.write(2, 'Fork failed!\n'.encode())
    sys.exit(0)
  elif rc == 0:
    # Do the prcess of the passed input parameters
    # os.write(1, 'Child!\n'.encode())
    
    if '>' in args:
      os.close(1)
      os.open(args[(args.index('>')+1)], os.O_CREAT | os.O_WRONLY)
      os.set_inheritable(1, True)
      args = args[:args.index('>')]
    elif '<' in args:
      os.close(0)
      os.open(args[(args.index('<')+1)], os.O_RDONLY)
      os.set_inheritable(0, True)
      del args[args.index('<')+1]
      del args[args.index('<')]
      
    execute_args(args)
  elif amper:
    pass
  else:
   os.wait()
    # os.write(1, 'Parent!\n'.encode())
  # os.write(1, input)
