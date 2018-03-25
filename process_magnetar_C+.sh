#!/bin/bash

# Changed to ON-CAL on Nov 29th morning

if [ $# -eq 0 ]
then
	echo "No arguments supplied"
	exit 0
fi

par2020=/beegfsBN/miraculix2/part0/src/B2020+28.par
par1745=/beegfsBN/miraculix2/part0/src/magnetar.par
datapath=/beegfsBN/miraculix2/part0/J1745-2900/Search/Effelsberg
date=$1

path1=/beegfs/R2FB0/$date/
path2=/beegfs/R2FB1/$date/
#echo $path

outdir=$datapath/$1_C+
echo $outdir
mkdir $outdir

#### First subband ####
outdirp0=$outdir/p0
mkdir $outdirp0
cd $outdirp0
dada2psrfits $path1/1745-2900/*_0000000000000000.000000.dada
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -P $par1745 -S 50 -b 2048 -t 10 $sfn
cd -
# Now process CAL
mkdir $outdirp0/CAL
cd $outdirp0/CAL
dada2psrfits $path1/1745-2900_ON_R/*_0000000000000000.000000.dada
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -C -F 1.0 -b 1024 -t 10 $sfn
cd -
# B2020
#mkdir $outdirp0/B2020+28
#cd $outdirp0/B2020+28
#dada2psrfits $path1/B2020+28/*16_0000000000000000.000000.dada -b
#fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
#fold_psrfits -P $par2020 -S 50 -b 1024 -t 10 $sfn
#cd -

#### second subband from second roach2, flip the band !
outdirp1=$outdir/p1
mkdir $outdirp1
cd $outdirp1
dada2psrfits  $path2/1745-2900/*_0000000000000000.000000.dada -i -f 7000
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -P $par1745 -S 50 -b 2048 -t 10 $sfn
cd -
# Now process CAL
mkdir $outdirp1/CAL
cd $outdirp1/CAL
dada2psrfits $path2/1745-2900_ON_R/*_0000000000000000.000000.dada -i -f 7000
fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
fold_psrfits -C -F 1.0 -b 1024 -t 10 $sfn 
cd -
# B2020
#mkdir $outdirp1/B2020+28
#cd $outdirp1/B2020+28
#dada2psrfits $path2/B2020+28/*16_0000000000000000.000000.dada -i -f 7000 -b
#fn=*fits;files=( $fn );sfn=$(sed 's/.\{10\}$//' <<< "$files")
#fold_psrfits -P $par2020 -S 50 -b 1024 -t 10 $sfn
#cd -


cd $outdir
psradd -R -m time -o $date.pcal $outdirp0/CAL/*cal*fits $outdirp1/CAL/*cal*fits 
#merge_psrfits $outdirp0/*_0001.fits $outdirp1/*_0001.fits

#fold_psrfits -b 2048 -S 100  -t 20 -P <parfile>
