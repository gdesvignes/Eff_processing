import os 
import glob
import sys

import shutil
import subprocess 
import pipes
import tarfile
import errno
from Queue import Queue
from threading import Thread


# THIS SCRIPT MODIFY THE HEADER of the output file
# - linear feed to circular
# - type poln for calibrators



NUM_THREADS = 8

q = Queue(maxsize=0)

def freq_combine(q):
    while True:
        cmd = q.get()
	os.system(cmd)
	q.task_done()



#def is_remote(host, path):
#    proc = subprocess.Popen(['ssh', host, 'test -d %s' % pipes.quote(path)])
#    proc.wait()
#    return proc.returncode == 0


BUF_DIR = "/beegfsBN/miraculix2/part0/J1745-2900/SP/Effelsberg"
TIMING_DIR = "/beegfsBN/miraculix2/part0/J1745-2900/Timing/Effelsberg"

#FREQS = {'60mm':'[4-5]???', '36mm':'8???', '20mm':'14???'}
#FREQS = {'60mm':'[4-5]???', '36mm':'8???'}
#FREQS = {'20mm':'14???'}
FREQS = {'60mm':'[4-5]???'}
#FREQS = {'36mm':'8???'}

SRCS = ['1745-2900', '1745-2900-ON_R', '1745-2900-OFF_R', \
	'B2020+28',  \
	'NGC7027-OFF_R', 'NGC7027-ON_R']
#SRCS = ['2205+6012', 'NGC7027-OFF_R', 'NGC7027-ON_R', '0355+54']
#SRCS = ['1745-2900-ON_R', '1745-2900-OFF_R']
#SRCS = ['1745-2900']
#xSRCS = ['B2020+28']

DEST_TAPE = "pulsar@archivesrv1:/srv/ivdfs_03/J1745-2900"

DOIT = False
DOIT = True



if len(sys.argv) < 2:
    print "Please provide a date in the form '20150302'" 
    sys.exit()


DATE = sys.argv[1]

datadir = os.path.join("/media/scratch/", DATE)

# Checking if given datadir exists on NODE 0 
#node = "pulsar@automatix0"
#if not is_remote(node, datadir):
##    print "Data directory '%s' on %s does not exist."%(datadir, node)
#    sys.exit()

# Create directory per source
destdir = os.path.join(BUF_DIR,DATE)
try:
    print 'Creating directory %s'%(destdir)
    if DOIT: os.mkdir(destdir)
except OSError as e:
    if e.errno == errno.EEXIST:
        print 'Directory %s already exists'%(destdir)
        pass
    else:
        raise

# Create directory per source
timingdir = os.path.join(TIMING_DIR,DATE)
try:
    print 'Creating directory %s'%(timingdir)
    if DOIT: os.mkdir(timingdir)
except OSError as e:
    if e.errno == errno.EEXIST:
        print 'Directory %s already exists'%(timingdir)
        pass
    else:
        raise

# Move to the BUFFER directory
try:
    print "Chdir to %s"%BUF_DIR
    os.chdir(BUF_DIR)
except:
    print "Could not chdir to %s"%BUF_DIR
    sys.exit()


for i in range(NUM_THREADS):
  worker = Thread(target=freq_combine, args=(q,))
  worker.setDaemon(True)
  worker.start()

## Loop over Freq and SRCs
for freq in sorted(FREQS.keys()):


  for src in SRCS:
    print '\nProcessing %s, frequency %s, files %s'%(src, freq, FREQS[freq])

    #if not 'OFF' in src: continue  ### GD HACK for speedup

    sdir = "%s/%s_%s"%(DATE,src,freq)

    # Destination directory
    destdir = os.path.join(BUF_DIR, sdir)


    # Join in frequency the data
    try:
        if 'ON' in src or 'OFF' in src:
            firstfreq = os.path.split(glob.glob("%s/????"%destdir)[0])[-1]
        else:
            firstfreq = os.path.split(glob.glob("%s/????/pulse*"%destdir)[0])[-1]
            tmp = glob.glob("%s/????/pulse*"%destdir)[0]
            firstfreq = tmp.split("/")[-2]
        print firstfreq
    except:
	print "NOT FOUND %s/????"%destdir
        continue
    print "Try to concatenate subbands %s/%s/*"%(destdir, firstfreq)
    if 'ON' in src or 'OFF' in src:
        fns = glob.glob("%s/%s/20*.ar"%(destdir, firstfreq))
    else:    
        fns = glob.glob("%s/%s/pulse*"%(destdir, firstfreq))
    fns.sort()

    for fn in fns:
          sfn = os.path.split(fn)[-1]
  	  if os.path.exists(os.path.join(destdir, sfn)): continue

          cmd = "psradd -R -o %s %s/%s/%s*"%(os.path.join(destdir, sfn), destdir, FREQS[freq], os.path.split(fn)[-1])
          print cmd
	  if DOIT: q.put(cmd)
    if DOIT: q.join()

    for fn in fns:
          sfn = os.path.split(fn)[-1]
	  # Reduce to 2048 bins (if magnetar obs) and set feed to circular
          if '1745-2900'== src:
	      if os.path.exists(os.path.join(destdir, sfn+'.b2048')): continue
	      cmd = "pam -d 1778 -e ar.b2048 --setnbin 2048 -C %s"%(os.path.join(destdir, sfn))
	  else:
	      cmd = "pam -m -C %s"%(os.path.join(destdir, sfn))
          print cmd
	  if DOIT: q.put(cmd)
    if DOIT: q.join()
   



    #"""
    if src=='1745-2900':
        print "Looking for %s/*.ar.b2048"%destdir
        fns = glob.glob("%s/*.ar.b2048"%destdir)
    else:
        print "Looking for %s/*.ar"%destdir
        fns = glob.glob("%s/*.ar"%destdir)
    fns.sort() 

    if not fns:
	continue

    destdir.replace("SP", "Timing")
    timingdir = os.path.join("/beegfsBN/miraculix2/part0/J1745-2900/Timing/Effelsberg", sdir)
    print timingdir

    try:
        print 'Creating directory %s'%(timingdir)
        if DOIT: os.mkdir(timingdir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print 'Directory %s already exists'%(timingdir)
            pass
        else:
            raise

    try:
	sfn = os.path.split(fns[0])[-1]
	print sfn
	#cmd = "psradd -o %s %s"%(os.path.join(destdir, src).replace('.ar', '_%s.ar'%freq), " ".join(fns))
	if not os.path.exists(os.path.join(timingdir, src)+ '_%s.ar'%freq):
	    cmd = "psradd -o %s %s"%(os.path.join(timingdir, src)+ '_%s.ar'%freq, " ".join(fns))
	    print cmd
	    if DOIT: os.system(cmd)

	# Change basis
	#cmd = "psredit -c rcvr:basis=circ -m  %s"%(os.path.join(timingdir, src)+ '_%s.ar'%freq)
	#print cmd
	#if DOIT: os.system(cmd)

	# Change basis
	if 'ON' in src or 'OFF' in src:
	  if 'NGC' in src and 'ON' in src:
	    cmd = "pam --type FluxCalOn -e pcal  %s"%(os.path.join(timingdir, src)+ '_%s.ar'%freq)
	  elif 'NGC' in src and 'OFF' in src:
	    cmd = "pam --type FluxCalOff -e pcal  %s"%(os.path.join(timingdir, src)+ '_%s.ar'%freq)
	  else:
	    cmd = "pam --type PolnCal -e pcal  %s"%(os.path.join(timingdir, src)+ '_%s.ar'%freq)
	  print cmd
	  if DOIT: os.system(cmd)
    except:
	raise
	pass
    #"""
