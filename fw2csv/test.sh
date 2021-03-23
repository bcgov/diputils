g++ cpp/dd_apply.cpp cpp/misc.cpp -o dd_apply.exe
tar xvf pnet.tar.gz
mv  ./moh_dip_pharmanet_dsp.rpt.csv tmp.csv
./dd_apply.exe moh_dip_pharmanet_dsp.rpt.dd moh_dip_pharmanet_dsp.rpt.dat
diff tmp.csv moh_dip_pharmanet_dsp.rpt.dat_dd_apply.csv
