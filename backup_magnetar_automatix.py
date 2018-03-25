import os
import sys
import tarfile
import glob

FREQS = {'60mm':'[4-5]???', '36mm':'8???'}

SRCS = ['1745-2900', '1745-2900-ON_R', '1745-2900-OFF_R', \
            'B2020+28', 'NGC7027-OFF_R', 'NGC7027-ON_R']

DOIT = True
BUF_DIR = "/beegfsBN/miraculix2/part0/J1745-2900/SP/Effelsberg"
DEST_TAPE = "pulsar@archivesrv1:/srv/ivdfs_03/J1745-2900"

if len(sys.argv) < 2:
    print "Please provide a date in the form '20150302'"
    sys.exit()


DATE = sys.argv[1]
destdir = os.path.join(BUF_DIR,DATE)
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
        ssdir = "%s/%s_%s_%s"%(DATE,DATE,src,freq)

        # No data, skip
        if not os.path.isdir(sdir):
            continue
            
        # Tar files
        tarname = "%s.tar"%(ssdir)
        if os.path.isfile(tarname):
            continue
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
