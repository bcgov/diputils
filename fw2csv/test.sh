g++ cpp/dd_apply.cpp cpp/misc.cpp -o dd_apply.exe # compile terminal utility
tar xvf pnet.tar.gz # extract test data
mv  ./moh_dip_pharmanet_dsp.rpt.csv tmp.csv # move already-converted (pre-computed) file to tmp.csv to check with our result
./dd_apply.exe moh_dip_pharmanet_dsp.rpt.dd moh_dip_pharmanet_dsp.rpt.dat # apply terminal utility
diff tmp.csv moh_dip_pharmanet_dsp.rpt.dat_dd_apply.csv # check to see if pre-computed result matches what we made
