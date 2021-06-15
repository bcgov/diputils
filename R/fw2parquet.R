# not a very efficient or useful operation. Proof of concept!
library(arrow) # https://arrow.apache.org/docs/r/
library(stringr)
library(data.table)

MAX_ROWS <- 10000000 # max rows per parquet file

pq_flush <- function(dat_file, fi, d_t){
  parquet_filename <- paste(dat_file, "_", sprintf('%07d', fi), ".parquet", sep = "")
  pq_sink <- FileOutputStream$create(parquet_filename)
  write_parquet(x=data.table(d_t), sink=pq_sink) # flush table d_t into numbered file
  pq_sink$close()
}

fw2parquet <- function(dat_file, dd_file) {
  dd = read.csv(dd_file) # read the data dictionary
  chunk <- sum(dd$Length) # length of one fixed-width record
  n_field <- length(dd$Length) # number of fields referenced in dd
  start <- dd$Start # start index for a field
  stop <- dd$Stop # stop index for a field
  label <- dd$Label # col names from dd
  f_idx <- 1:n_field # field indices
  con <- file(dat_file, open = "r") # connection to fixed-width file, zipped or not!
  ci <- 1 # current row index, this table-buffer-- buffer some lines in a table
  fi <- 1 # parquet file counter
  pq_writer <- NULL # parquet writer object
  d_t <- NULL # empty data table

  while(1){
    if(ci %% 111 == 0) print(paste("line_idx= ", ci, sep="")) # crude progress bar

    line <- readChar(con, chunk, useBytes = FALSE) # read a line of fw data
    if (identical(line, character(0))) break # read line-by-line until End Of File
    
    row <- c(n_field) # create a vector for one row
    for(i in f_idx) row[i] <- trimws(substring(line, strtoi(start[[i]]), strtoi(stop[[i]])))
   
    if(ci == 1) d_t = NULL # empty data table

    if(is.null(d_t)) d_t = row # table starts with one row
    else d_t = rbind(d_t, row) # d_t = rbind(d_t, t(row))

    if (ci == MAX_ROWS){
      colnames(d_t) <- label # if we have enough rows, write what we have to numbered file
      pq_flush(dat_file, fi, d_t)
      fi = fi + 1
      ci = 1
    } 
    else ci <- ci + 1
  } 
  
  colnames(d_t) <- label 
  pq_flush(dat_file, fi, d_t) # flush the remaining lines in the buffer
  close(con)  # close connection to gzip file
}
