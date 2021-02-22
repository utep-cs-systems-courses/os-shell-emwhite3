#! /usr/bin/env python3

import os, sys, re, fileinput

def check_ps1():
  if len(os.environ['PS1']) < 20 and len(os.environ['PS1']) >= 0:
    return os.environ['PS1']
  return '$ '

def read_input():
  os.write(1, check_ps1().encode())
  input = os.read(0, 1000)
  if input == '\n'.encode():
    read_input()
  return re.split(' ', input.decode('utf-8')[0:-1])

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
      os.write(2, ('Program terminated with exit code %s\n'%str(e)).encode())
      sys.exit(1)
      
  os.write(2, ('%s: command not found\n'%args[0]).encode())
  sys.exit(1)

args = []
pipe = False
while 1:
  amper = False
  if not pipe:
    args = read_input()
  if args[0] == 'exit':
    os.write(1, 'Goodbye!\n'.encode())
    sys.exit(0)
  elif args[0] == 'cd':
    os.chdir(args[1])
    continue
  elif args[-1] == '&':
    args = args[:-1]
    amper = True
  elif '|' in args and not pipe:
    pr, pw = os.pipe()
    for fd in (pr, pw):
      os.set_inheritable(fd, True)

  rc = os.fork()
  
  if rc < 0:
    os.write(2, 'Fork failed!\n'.encode())
    sys.exit(0)
  elif rc == 0:
    if '|' in args:
      os.close(1)
      dup = os.dup(pw)
      for fd in (pr, pw):
        os.close(fd)
      os.set_inheritable(dup, True)
      args = args[:args.index('|')]
    if pipe:
      os.close(0)
      dup = os.dup(pr)
      for fd in (pr, pw):
        os.close(fd)
      os.set_inheritable(dup, True)
    elif '>' in args:
      os.close(1)
      os.open(args[(args.index('>')+1)], os.O_CREAT | os.O_WRONLY)
      os.set_inheritable(1, True)
      del args[args.index('>')+1]
      del args[args.index('>')]
    elif '<' in args:
      os.close(0)
      os.open(args[(args.index('<')+1)], os.O_RDONLY)
      os.set_inheritable(0, True)
      del args[args.index('<')+1]
      del args[args.index('<')]
    elif '|' in args:
      pr, pw = os.pipe()
      
    execute_args(args)

  elif amper:
    pass
  elif not pipe and '|' in args:
    os.wait()
    args = args[(args.index('|')+1):]
    pipe = True
  elif pipe and not ('|' in args):
    pipe = False
    print(os.read(pr, 10000).decode())
    for fd in (pw, pr):
      os.close(fd)
    #os.fdopen(0)
  else:
   os.wait()
    # os.write(1, 'Parent!\n'.encode())
  # os.write(1, input)
