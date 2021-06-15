/* qa.c: check number of fields per line in csv file..
based on lc.c:
     "20190602 use C to count lines in a file that have some non-space
     character in them.. similar but distinct from "wc -l" in linux" */
#include"misc.h"
#include"string.h"
#define MAXCHAR 1024 * 64 // flat file line not likely longer than this? 

int main(int argc, char ** argv){
  if(argc < 2){
    printf("lc.c: non-white row (AND field) count for file\n\tUsage: qa [filename]\n");
    exit(1);
  }
  FILE *fp;
  char str[MAXCHAR];
  char* filename = argv[1];
  fp = fopen(filename, "r");

  if(fp == NULL){
    printf("Error: could not open file: %s\n", filename);
    exit(1);
  }

  long unsigned int lc = 0;
  unsigned int i;
  int has_nonspace, comma_count, n_fields;
  while(fgets(str, MAXCHAR, fp)){
    has_nonspace = false;
    comma_count = 0;
    for(i = 0; i < strlen(str); i++){
      if(!isspace(str[i])) has_nonspace = true;
      if(str[i] == ',') comma_count ++;
    }
    if(lc == 0){
      n_fields = comma_count + 1;
    }
    else{
      if(comma_count + 1 != n_fields){
        printf("comma count: %d\n", comma_count);
        printf("n_fields: %d\n", n_fields);
        printf("lc %ld\n", lc);
        err("unexpected number of fields this row");
      }
    }
    if(has_nonspace) lc ++;
  }
  fclose(fp);
  printf("lines,%ld\n", lc);
  return 0;
}
