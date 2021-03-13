test ! -f moh_dip_pharmanet_dsp.rpt.dat && tar xvf pnet.tar.gz
test ! -f conversion.exe && g++ -O3 cpp/conversion.cpp -o conversion.exe -larrow
test ! -f dd_apply.exe && g++ -O3 cpp/dd_apply.cpp cpp/misc.cpp -o dd_apply.exe -larrow -lparquet
./dd_apply.exe moh_dip_pharmanet_dsp.rpt.dd moh_dip_pharmanet_dsp.rpt.dat
