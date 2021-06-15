#ifndef _MISC_H_
#define _MISC_H_
//---------------------------------------------------------------------------//
// misc.h: helper functions //
// date: 20190302 //
//---------------------------------------------------------------------------//
#include<stdio.h>
#include<stdlib.h>
#include<memory.h>
#include<time.h>
#include<search.h>
#include<string.h>
#include<ctype.h>
// memory handles vs. file handles: need to generalize this

/* shorthand for for loops from 0 to N */
#define for0(i,n) for(i = 0; i < n; i++)

/* can increase limits if necessary */
#define MAX_ALLOC 1024

/* file and memory handles */
void * alloc_open[MAX_ALLOC];
unsigned int n_alloc_open;

/* message and quit */
void err(const char * msg){
  printf("Error: %s\n", msg);
  exit(1);
}

/* allocate memory */
inline void * alloc(size_t nb, int free_later){
  void * d = malloc(nb);
  if(!d){
    printf("%zu\n", nb);
    err("failed to allocate memory");
  }
  memset(d, '\0', nb);
  // printf("alloc %zu bytes\n", nb);
  if(free_later) alloc_open[n_alloc_open ++] = d;
  return d;
}

/* remember this allocation, autofree it later.. */
inline void * alloc(size_t nb){
  return alloc(nb, true);
}

/* temporary allocation, need to free explicitly */
inline void * alloc_tmp(size_t nb){
  return alloc(nb, false);
}

/* get size of file pointer */
size_t size(FILE * f){
  fseek(f, 0L, SEEK_END);
  size_t sz = ftell(f);
  rewind(f);
  return sz;
}

/* open a file */
FILE * open(char * fn){
  FILE * f = fopen(fn, "rb");
  if(!f){
    printf("Filename: %s\n", fn);
    err("failed to open file");
  }
  return f;
}

/* close a file */
inline void close(FILE * f){
  fclose(f);
}

/* try opening and closing to assert file exists */
int exists(char * fn){
  close(open(fn));
  return true;
}

/* get the size of a file */
size_t fsize(char * fn){
  FILE * f = open(fn);
  size_t s = size(f);
  close(f);
  return s;
}

void init(){
  n_alloc_open = 0;
}

int quit(){
  register unsigned int i;
  for0(i,n_alloc_open) free(alloc_open[i]);
  return 0;
}

char * fread(char * fn){
  size_t s = fsize(fn);
  char * d = (char *)alloc_tmp(s);
  fread(d, s, 1, open(fn));
  return d;
}

inline char * getline(FILE * f, int persist){
  size_t start = ftell(f);
  while(fgetc(f) != '\n'){
  }
  size_t len = ftell(f) - start;
  fseek(f, start, SEEK_SET);

  char * dat = (char *) alloc(len + 1, persist); // null-terminate, to be safe
  size_t nr = fread(dat, len, 1, f);
  if(nr != 1) err("incorrect number of bytes read");
  dat[len] = '\0';
  return dat;

}

char * trim(char * s);

/* c impl. of python split: assume comma delim. s: string, len: length of s, n_f_expect: number of fields expected */
inline char ** split(char * s, unsigned int len, unsigned int & n_f_expect){

  /* count the fields first */
  if(len < 1) return NULL;

  trim(s);

  unsigned int n_f = 1;
  register unsigned int i = 0;

  for0(i, len) if(s[i] == ',') n_f ++;

  if(n_f_expect == 0) n_f_expect = n_f; // assume no stray commas in header file
  if(n_f != n_f_expect){
    printf("WARNING: n_f %d nf_exp %d line: '%s'\n", n_f, n_f_expect, s);
    return NULL; //err("unexpected # of fields\n");
  }
  char ** ss = (char **) alloc_tmp(sizeof(char *) * n_f);

  register unsigned int j, s_len, k;
  j = 0;
  // for each field
  for0(i, (n_f - 1)){
    s_len = j;
    while(s[j] != ',' && s[j] != '\n') j ++;

    s_len = j - s_len;
    j -= s_len;
    ss[i] = (char *) alloc_tmp(sizeof(char *) * (s_len + 1));
    char * sss = ss[i];
    for0(k, s_len) sss[k] = s[j ++];
    sss[s_len] = '\0';
    // printf("\t[%s]\n", sss);
    j ++; // jump over the comma
  }

  // don't forget to process last field! process it separately
  i = n_f - 1;
  s_len = j;
  while(s[j] != '\n' && s[j] != '\0') j ++;

  s_len = j - s_len;
  j -= s_len;
  ss[i] = (char *) alloc_tmp(sizeof(char *) * (s_len + 1));
  char * sss = ss[i];
  for0(k, s_len) sss[k] = s[j++];
  sss[s_len] = '\0';

  return ss;
}

void split_print(char ** ss, int n_f){
  int i;
  printf("[");
  for0(i, (n_f-1)) printf("'%s' ", ss[i]);
  printf("'%s']\n", ss[n_f - 1]);
}

void free_split(char ** ss, int n_f){
  register int i;
  for0(i, n_f) free(ss[i]);
  free(ss);
}

// http://www.gnu.org/software/libc/manual/html_node/Tree-Search-Function.html
typedef struct{
  char * key;
  //long unsigned int value
}
str_map; //str_luint_map;

int compare(const void *a, const void *b){
  const str_map * lm = (const str_map* ) a;
  const str_map * lr = (const str_map* ) b;
  return strcmp(lm->key, lr->key);
}

unsigned int tree_count;
void action(const void *r, const VISIT which, const int depth){
  str_map * x = (str_map *) r;
  switch (which) {
    case preorder:
    break;
    case endorder:
    break;
    case postorder:
    case leaf:
    printf("%s\n", x->key);
    break;
  }
}

/* tsearch - find and create if not exist
tfind - find but don't create if not exist
tdelete - delete an entry */

char * trim(char * str){
  size_t len = 0;
  char *frontp = str;
  char *endp = NULL;

  if(str == NULL) return NULL;
  if(str[0] == '\0') return str;

  len = strlen(str);
  endp = str + len;

  /* Move front and back pts to address the first non-whitesp chars from each end. */
  while(isspace(((unsigned char) *frontp))){
	  ++ frontp;
  }
  if(endp!=frontp){
    while(isspace(((unsigned char) *(--endp))) && endp != frontp){
    }
  }

  if( str + len - 1 != endp ) *(endp + 1) = '\0';
  else if( frontp != str && endp == frontp ) *str = '\0';

  /* Shift string so it starts at str so if it's dynamically alloc. we can still free it on the returned pointer..
  ..Note the reuse of endp to mean the front of the string buffer now. */
  endp = str;
  if( frontp != str ){
    while( *frontp ) *endp++ = *frontp++;
    *endp = '\0';
  }

  return str;
}

#endif
