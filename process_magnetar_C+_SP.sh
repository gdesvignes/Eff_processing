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

period=3.8
par1745=/beegfsBN/miraculix2/part0/src/magnetar.par
datapath=/beegfsBN/miraculix2/part0/J1745-2900/Search/Effelsberg
date=$1
#echo $path

outdir=$datapath/$1_C+
combined_dir=$outdir/combined_SP
echo $outdir
mkdir $outdir
mkdir $combined_dir
mkdir /dev/shm/$1_C+/

#### First subband ####
outdirp0=$outdir/p0/SP
mkdir $outdirp0
cd $outdirp0
echo cd $outdirp0
fn=../*5000_0001.fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -P $par1745 -S 0.08 -b 2048 -t $period $sfn -o /dev/shm/$1_C+/SP_5000
mv /dev/shm/$1_C+/SP_5000*fits .
cd -

#### second subband from second roach2, flip the band !
outdirp1=$outdir/p1/SP
mkdir $outdirp1
cd $outdirp1
echo cd $outdirp1
fn=../*7000_0001.fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -P $par1745 -S 0.08 -b 2048 -t $period $sfn -o /dev/shm/$1_C+/SP_7000
mv /dev/shm/$1_C+/SP_7000*fits .
cd -

#psradd the bands
#nb=$(ls $outdirp1/*.fits | wc -l)
for f in $(seq -w 1 1000)
do
	if [ ! -f $combined_dir/SP_$f.zap.f8 ]; then
		psradd -E $par1745 -R -o SP_$f.ar $outdirp0/SP_5000_$f.fits $outdirp1/SP_7000_$f.fits -o /dev/shm/$1_C+/SP_$f.ar
		pac -A $outdir/*pcal /dev/shm/$1_C+/SP_$f.ar
		/beegfsBN/miraculix2/part0/src/zap.psh -e zap /dev/shm/$1_C+/SP_$f*.calibP
		pam -f 8 -e zap.f8 /dev/shm/$1_C+/SP_$f*.zap
		mv /dev/shm/$1_C+/SP_$f.* $combined_dir/.
	fi
done

# Now  CALibrate

