# fw2csv
Fixed width to csv converter. Doesn't use memory so it won't bonk on a large file. However, run it on an SSD or faster storage or it will be slow. [Click here to see elegant C++ code](https://github.com/bcgov/diputils/blob/master/fw2csv/cpp/dd_apply.cpp)

## setup
For MacOS type:
```
sudo brew install gcc
```

to install gnu c++ compiler (g++).

## test
To run the test, type:
```
./test.sh
```
 
Test should have succeded if you see:
```
x ./moh_dip_pharmanet_dsp.rpt.csv
x ./moh_dip_pharmanet_dsp.rpt.dat
x ./moh_dip_pharmanet_dsp.rpt.dd
data dictionary file: moh_dip_pharmanet_dsp.rpt.dd
data input file: moh_dip_pharmanet_dsp.rpt.dat
output file: moh_dip_pharmanet_dsp.rpt.dat_dd_apply.csv
start: ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100', '110', '120', '130', '140', '150', '160', '170', '180', '190', '200']
stop: ['9', '19', '29', '39', '49', '59', '69', '79', '89', '99', '109', '119', '129', '139', '149', '159', '169', '179', '189', '199', '209']
length: ['10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10', '10']
label: ['DE.STUDYID', 'DE.CLNT_GENDER_LABEL', 'DE_DM_CL.MRG_CLNT_BRTH_MTH', 'DE_DM_CL.AGE_AT_SERVICE_YEAR', 'DE_CL_GEO.CLNT_HA_AREA_CD', 'DE_CL_GEO.CLNT_LHA', 'DE.FCTY_LABEL*', 'DE_FC_GEO.FCTY_HA_AREA_CD', 'DE_FC_GEO.FCTY_LHA', 'DE_PR_PRAC.PRSCR_PRAC_IDNT*', 'DE_PR_GEO.PRSCR_PRAC_HA_AREA_CD', 'DE_PR_GEO.PRSCR_PRAC_LHA', 'DE_PR_PRAC.PRSCR_PRAC_LIC_BODY_IDNT', 'DE_PR_INFO.PRSCR_SPTY_FLG', 'DE_PR_INFO.RCNT_CLG_SPTY_1_LABEL', 'DE_PR_INFO.RCNT_CLG_SPTY_2_LABEL', 'DE.HLTH_PROD_LABEL', 'DE.SRV_DATE', 'DE.DSPD_QTY', 'DE.DSPD_DAYS_SPLY', 'DE.DRUG_USE_DIR']
```
