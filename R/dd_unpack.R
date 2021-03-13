# unpack data dictionaries in .xls files, into csv files. usage: Rscript dd_unpack.R [name of Excel file to unpack]
library(readxl)

fn<-""
args = commandArgs(trailingOnly=TRUE)

if(length(args)>=1) fn<-args[1]
if(length(args)==0) stop("Error: usage: Rscript dd_unpack.R [data dictionary file.xls/xlsx]")

for(s in excel_sheets(fn)){
  out_fn<-paste(paste(fn, s, sep="_"), ".csv", sep="");
  write.csv(read_excel(fn, sheet=s, skip=1), out_fn);
}
