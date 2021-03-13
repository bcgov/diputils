/* From https://arrow.apache.org/docs/cpp/parquet.html
  The arrow::WriteTable() function writes an entire ::arrow::Table to an output file. */
#include <arrow/api.h>
#include <parquet/arrow/writer.h>

void write_parquet(){
   std::shared_ptr<arrow::io::FileOutputStream> outfile;
   PARQUET_ASSIGN_OR_THROW(
      outfile,
      arrow::io::FileOutputStream::Open("test.parquet"));

   PARQUET_THROW_NOT_OK(
      parquet::arrow::WriteTable(table, arrow::default_memory_pool(), outfile, 3));
}

int main(int argc, char ** argv){
return 0;
}



