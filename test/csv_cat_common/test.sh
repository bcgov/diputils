# testing concatenating a short section of large csv files (incl. header) together

mkdir -p test
rm -f csv_cat_common_fields.csv

# csv_cat_common_fields dsp_rpt.dat_dd_sliceapply.csv clm_rpt_1995_2000.dat_dd_sliceapply.csv clm_rpt_2001_2005.dat_dd_sliceapply.csv clm_rpt_2006_2010.dat_dd_sliceapply.csv clm_rpt_2011_2014.dat_dd_sliceapply.csv clm_rpt_2015_2018.dat_dd_sliceapply.csv

head -5 clm_rpt_1995_2000.dat_dd_sliceapply.csv > test/1.csv
head -5 clm_rpt_2001_2005.dat_dd_sliceapply.csv > test/2.csv
head -5 clm_rpt_2006_2010.dat_dd_sliceapply.csv > test/3.csv
head -5 clm_rpt_2011_2014.dat_dd_sliceapply.csv > test/4.csv
head -5 clm_rpt_2015_2018.dat_dd_sliceapply.csv > test/5.csv
head -5 dsp_rpt.dat_dd_sliceapply.csv > test/6.csv

cd ./test
csv_cat_common_fields 6.csv 1.csv 2.csv 3.csv 4.csv 5.csv
cd ..
