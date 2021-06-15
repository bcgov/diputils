/* 20190602 count lines in a file, that have some non-space character in them..
..similar to "wc -l" in linux */
#include"misc.h"
#include"string.h"
#define MAXCHAR 1024*1024

int main(int argc, char ** argv){
  if(argc < 2){
    printf("lc.c: non-white row count for file\n\tUsage: lc [filename]\n");
    exit(1);
  }
  FILE *fp;
  char str[MAXCHAR];
  char* filename = argv[1];
  fp = fopen(filename, "r");

  if (fp == NULL){
    printf("Error: could not open file: %s\n", filename);
    exit(1);
  }

  long int lc = 0;
  unsigned int i;
  while(fgets(str, MAXCHAR, fp)){
    for(i = 0; i < strlen(str); i++){
      if(!isspace(str[i])){
        lc++;
        break;
      }
    }
  }
  fclose(fp);
  printf("%ld\n", lc);
  return 0;
}
