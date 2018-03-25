#!/bin/bash

#test=p0/*fits
#files=( $test )
#echo $files
#nfiles=${#files[@]}
#echo $files
#var1=$(sed 's/.\{10\}$//' <<< "$files")
#echo $var1

if [ $# -eq 0 ]
then
	echo "No arguments supplied"
	exit 0
fi

SRC=2205+6012
SRC=1746-2849
SRC=1746-2856
SRC=1810-197

parSRC=/beegfsBN/miraculix2/part0/gdesvignes/$SRC.par
datapath=/beegfsBN/miraculix2/part0/gdesvignes/$SRC

date=$1
path1=/beegfs/R2FB0/$date/
path2=/beegfs/R2FB1/$date/

# Create output directories
mkdir $datapath
outdir=$datapath/$1_C+
mkdir $outdir

# Get RA and DEC from parfile
ra=`grep RAJ $parSRC  | awk '{print $2}'`
dec=`grep DECJ $parSRC  | awk '{print $2}'`

#### First subband ####
outdirp0=$outdir/p0
mkdir $outdirp0
cd $outdirp0
#dada2psrfits $path1/$SRC/*_0000000000000000.000000.dada -p $SRC -r $ra -d $dec
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
#fold_psrfits -P $parSRC -S 50 -b 2048 -t 20 $sfn
cd -

# Now process CAL
mkdir $outdirp0/CAL
cd $outdirp0/CAL
#dada2psrfits $path1/$SRC-ON_R/*_0000000000000000.000000.dada -p $SRC -r $ra -d $dec
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
#fold_psrfits -C -F 1.0 -b 1024 -t 10 $sfn
cd -

#### second subband from second roach2, flip the band !
outdirp1=$outdir/p1
mkdir $outdirp1
cd $outdirp1
dada2psrfits  $path2/$SRC/*_0000000000000000.000000.dada -p $SRC -r $ra -d $dec -i -f 7000
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -P $parSRC -S 50 -b 2048 -t 20 $sfn
cd -
# Now process CAL
mkdir $outdirp1/CAL
cd $outdirp1/CAL
dada2psrfits $path2/$SRC-ON_R/*_0000000000000000.000000.dada -p $SRC -r $ra -d $dec -i -f 7000
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -C -F 1.0 -b 1024 -t 10 $sfn 
cd -


cd $outdir
psradd -R -m time -o $date.pcal $outdirp0/CAL/*cal*fits $outdirp1/CAL/*cal*fits 
#merge_psrfits $outdirp0/*_0001.fits $outdirp1/*_0001.fits

#fold_psrfits -b 2048 -S 100  -t 20 -P <parfile>
