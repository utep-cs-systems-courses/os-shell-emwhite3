#! /usr/bin/env python3

import os, sys, re, time


# check if the set ps1 is set and not too long
def check_ps1():
  try:
    if len(os.environ['PS1']) < 20 and len(os.environ['PS1']) >= 0:
      return os.environ['PS1']
  except KeyError:
    return '$ '
  return '$ '


# reads input from fd 0 from user
def my_read_line():
  os.write(1, check_ps1().encode())
  input = os.read(0, 1000)
  if input == '\n'.encode():
    my_read_line()
  return re.split(' ', input.decode('utf-8')[0:-1])


# executes the child process given args for the program
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

# set args and pipe before loop since
# they are modified in the loop
args = []
pipe = False
while 1:
  amper = False
  print('top of loop', args)
  print('pid', os.getpid())
  if not pipe:			      # these are the checks for 'special' commands
    args = my_read_line()
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
  				                  
  rc = os.fork()            # fork here to the child process with gathered information
  
  if rc < 0:			          # if the fork failed notify the user
    os.write(2, 'Fork failed!\n'.encode())
    sys.exit(0)
  elif rc == 0:			        # this is the child process
    if pipe or '|' in args:	# check if we are a reading writing or both pipe command
      if pipe:			        # set appropriate fds for reading and writing to a pipe
        #print(os.read(pr, 10000))
        print(args)
        print('in last command')
        os.close(0)
        dup_r = os.dup(pr)
        os.close(pr)
        os.set_inheritable(dup_r, True)
      if '|' in args:
        os.close(1)
        dup_w = os.dup(pw)
        os.close(pw)
        os.set_inheritable(dup_w, True)
        args = args[:args.index('|')]
      
      
      
    elif '>' in args:		      # check if we have output redirect and set fds
      os.close(1)
      os.open(args[(args.index('>')+1)], os.O_CREAT | os.O_WRONLY)
      os.set_inheritable(1, True)
      del args[args.index('>')+1]
      del args[args.index('>')]
    elif '<' in args:		      # check if we have input redirect and set fds
      os.close(0)
      os.open(args[(args.index('<')+1)], os.O_RDONLY)
      os.set_inheritable(0, True)
      del args[args.index('<')+1]
      del args[args.index('<')]
    
    execute_args(args)		    # execute the child process

  elif amper:			            # parent checks
    pass			                # if we want a background process do not wait for child to finish
  elif '|' in args:		        # if we are a write process set args for next child process
    os.wait()
    args = args[(args.index('|')+1):]
    print("passing last args: ", args)
    pipe = True
  elif pipe:
    #print(os.read(pr, 10000).decode())
    os.wait()
    print('in pipe elif')
    pipe = False
  else:				                # wait for child process to finish
    os.wait()
