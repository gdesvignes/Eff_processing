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

NUM_THREADS = 10

def freq_combine(q):
    while True:
        cmd = q.get()
	os.system(cmd)
	q.task_done()

q = Queue(maxsize=0)


#def is_remote(host, path):
#    proc = subprocess.Popen(['ssh', host, 'test -d %s' % pipes.quote(path)])
#    proc.wait()
#    return proc.returncode == 0


BUF_DIR = "/beegfsBN/miraculix2/part0/J1745-2900/SP/Effelsberg"

FREQS = {'60mm':'[4-5]???', '36mm':'8???', '20mm':'14???'}
#FREQS = {'36mm':'8???', '20mm':'14???'}
FREQS = {'60mm':'[4-5]???', '36mm':'8???'}
FREQS = {'60mm':'[4-5]???'}

SRCS = ['1745-2900', '1745-2900-ON_R', '1745-2900-OFF_R', \
	#'B2020+28', 'B2021+51', 'B0355+54', 'B1937+21', 'B1642-03', 'NGC7027-OFF_R', 'NGC7027-ON_R']
	'2020+28', 'NGC7027-OFF_R', 'NGC7027-ON_R']

#SRCS = ['2205+6012', 'NGC7027-OFF_R', 'NGC7027-ON_R', '0355+54']
#SRCS = ['B2020+28']

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

# Move to the BUFFER directory
try:
    print "Chdir to %s"%BUF_DIR
    os.chdir(BUF_DIR)
except:
    print "Could not chdir to %s"%BUF_DIR
    sys.exit()


## Loop over Freq and SRCs
for freq in sorted(FREQS.keys()):

  print 'Processing frequency %s, files %s'%(freq, FREQS[freq])

  for src in SRCS:


    sdir = "%s/%s_%s"%(DATE,src,freq)

    # Destination directory
    destdir = os.path.join(BUF_DIR, sdir)


    # Create directory per source
    try:
	print 'Creating directory %s'%(destdir)
        if DOIT: os.mkdir(destdir)
    except OSError as e:
        if e.errno == errno.EEXIST:
	    print 'Directory %s already exists'%(destdir)
            pass
        else:
            raise


    # Loop over all automatixes to rsync the data
    for ii in range(4,16):
	node = "pulsar@automatix%d"%ii
	ssrcdir = os.path.join(datadir, src)
	srcdir = os.path.join(datadir, src, FREQS[freq])

	#if not is_remote(node, ssrcdir):
	#    print "Data directory '%s' on %s does not exist. Skipping..."%(ssrcdir, node)
	#else:
	cmd = "rsync --stats -a --rsh=\"ssh -c blowfish\"  -e \"ssh pulsar@asterix ssh\" %s:%s %s"% (node, srcdir, destdir)
        cmd = "rsync --stats -a %s:%s %s"% (node, srcdir, destdir)
	print cmd
	if DOIT: os.system(cmd)

    # Check how many files were copied
    print 'Looking at copied dirs %s'%(os.path.join(destdir, FREQS[freq]))
    copied_dirs = glob.glob(os.path.join(destdir, FREQS[freq]))
    
    if not copied_dirs:
	print "No files from %s at %s"%(src, freq)
        # Cleanup intermediary files
        print "Removing directory %s"%destdir
        if DOIT: shutil.rmtree(destdir)
        continue
    """
    if 0:
	    # Tar files
	    tarname = "%s.tar"%(sdir)
	    print "Creating tar file %s from %s"%(tarname, sdir)
	    if DOIT:
		tf = tarfile.open(tarname, mode="w") 
		tf.add(sdir)
		tf.close()

	    # Copy tarfile to Tape
	    fns = glob.glob(os.path.join(BUF_DIR, tarname))
	    print "Found %d archive to backup to %s"%(len(fns), DEST_TAPE)

	    if len(fns) != 1:
		print 'Error: Found ', fns
		print "Exiting.."

	    else:
		cmd = "rsync -av %s %s"%(" ".join(fns), DEST_TAPE)
		print cmd
		if DOIT: os.system(cmd)


    
    # Psradd the data
    firstfreq = os.path.split(glob.glob("%s/????"%destdir)[0])[-1]
    fns = glob.glob("%s/%s/*"%(destdir, firstfreq))
    fns.sort()
    print "Try to concatenate subbands %s/%s/*"%(destdir, firstfreq)

    if DOIT:
	for i in range(NUM_THREADS):
	  worker = Thread(target=freq_combine, args=(q,))
	  worker.setDaemon(True)
	  worker.start()

    for fn in fns:
        sfn = os.path.split(fn)[-1]
	if os.path.exists(os.path.join(destdir, sfn)): continue
        cmd = "psradd -R -o %s %s/%s/%s"%(os.path.join(destdir, sfn), destdir, FREQS[freq], os.path.split(fn)[-1])
        #print cmd
        #if DOIT: os.system(cmd)
        #os.system(cmd)

	q.put(cmd)

    q.join()
    """
   



    """
    fns = glob.glob("%s/*.ar"%destdir)
    fns.sort() 
    print "Adding %s files together from %s/*.ar"%(" ".join(fns), destdir)
    try:
	    sfn = os.path.split(fns[0]) 
	    cmd = "psradd -R -m time -o %s %s"%(os.path.join(destdir, sfn).replace('.ar', '_%s.ar'%freq), " ".join(fns))
	    print cmd
	    if DOIT: os.system(cmd)
	    #os.system(cmd)
    except:
	    pass
    """

    # Copy psradded data to miraculix
    #fns = glob.glob(os.path.join(destdir, '*.ar'))
    #cmd = "rsync -a --progress %s %s"%(" ".join(fns), DEST_MIRACULIX)
    #print cmd
    #if DOIT: os.system(cmd)
    

    # Cleanup intermediary files
    #print "Removing directory %s"%destdir
    #if DOIT: shutil.rmtree(destdir)
