// Copyright 2019 Province of British Columbia
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/* an in-progress graphical interface (not completed) for force-based layout
 of clustering algorithm results */
#include"glut.h"
priority_queue<f_i> dmat;
map<size_t, size_t> meta;
// map<size_t, size_t> up;
map<size_t, size_t> p_count;

GLvoid resize(GLsizei w, GLsizei h){
  GLfloat ratio;
  glViewport(0, 0, w, h);
  // Select projection matrix
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  getMatrix();

  // Adjust viewing volume (orthographic)
  // If taller than wide adjust y
  if(w < h){
    ratio = (GLfloat) h/ (GLfloat) w;
    glOrtho(-1.0f, 1.0f, -1.0f * ratio, 1.0f * ratio, -1.0f, 1.0f);
    _bottom = -1. * ratio; _top = 1. * ratio;
    _left = -1.; _right = 1.;
  }
  // If wider than tall adjust x
  else if (h <= w){
    ratio = (GLfloat) w / (GLfloat) h;
    glOrtho(-1.0f * ratio, 1.0f * ratio, -1.0f, 1.0f, -1.0f, 1.0f);
    _left = -1. * ratio; _right = 1. * ratio;
    _bottom = -1.; _top = 1.;
  }

  glMatrixMode(GL_MODELVIEW);
  //glLoadIdentity();
  //getMatrix();
}

GLvoid initializeGL(GLsizei width, GLsizei height){
}

void polarView(GLdouble radius, GLdouble twist, GLdouble latitude,
GLdouble longitude){
  glTranslated(0.0, 0.0, -radius);
  glRotated(-twist, 0.0, 0.0, 1.0);
  glRotated(-latitude, 1.0, 0.0, 0.0);
  glRotated(longitude, 0.0, 0.0, 1.0);
}
inline float sgn(float x){
  return x < 0 ? -1.: 1.;
}

inline float clamp(float x, float T){
  return (abs(x) > abs(T)) ? sgn(x) * abs(T) : x;
}
inline vec3 clamp(vec3& x, float T){
  return vec3(clamp(x.x, T), clamp(x.y, T), clamp(x.z, T));
}

void iterate(){
  long unsigned int n_arrow = arrow_head.size();
  if(n_arrow != arrow_tail.size()) err("arrow array size mismatch");
  long unsigned int i, j, src, dst;

  float xmin, xmax, ymin, ymax, zmin;
  xmin = ymin = FLT_MAX;
  xmax = ymax = FLT_MIN;
  for0(i, sphere_pos.size()){
    float x = sphere_pos[i].x;
    float y = sphere_pos[i].y;
    if(x < xmin) xmin = x;
    if(x > xmax) xmax = x;
    if(y < ymin) ymin = y;
    if(y > ymax) ymax = y;
  }

  for0(i, sphere_pos.size()){
    // optional scaling
    sphere_pos[i].x -= xmin;
    sphere_pos[i].x *= (1. / (xmax-xmin));

    sphere_pos[i].y -= ymin;
    sphere_pos[i].y *= (1./(ymax-ymin));

  }

  return;

  // sphere repulsion force (should multicore these ASAP)
  float d_max = 1.;
  float f = 0.05;
  for0(i, n_arrow){
    src = arrow_tail[i];
    dst = arrow_head[i];
    vec3 d(sphere_pos[src] - sphere_pos[dst]);
    if(d.length() < 50. * SPHERE_RADIUS){
      d = d * 0.00003;

      sphere_pos[src] += d;
      sphere_pos[dst] -= d;
    }
    else{
      // arrow spring force
      float fd = d.length() - 5. * SPHERE_RADIUS;
      fd = sqrt(fd * fd);
      vec3 ux((d/d.length()) * 0.025 * fd);
      if(ux.length() > SPHERE_RADIUS / 2.){
        sphere_pos[src] -= ux;
        sphere_pos[dst] += ux;
      }
    }
  }
}

void renderBitmapString(float x, float y, const char *string){
  glRasterPos2f(x,y);
  /*
  HDC ghDC;
  HGLRC ghRC;
  */
  SelectObject(ghDC, GetStockObject(SYSTEM_FONT));
  wglUseFontBitmaps(ghDC, 0, 255, 1000);
  glListBase(1000);
  glCallLists(strlen(string), GL_UNSIGNED_BYTE, string); //"Click on node: show common vs. different, plus. merge (bridge) node info!");
}

void drawString(){
  renderBitmapString(20, 20, NULL);
}

/* rendering method */
GLvoid draw(int p_select){
  iterate();
  int draw_text = true;

  int debug = false;
  if(debug){
    if(sphere_pos.size() < 1){
      // add two spheres!
      sphere_pos.push_back(vec3(2, 2, 2)); sphere_col.push_back(vec3(2, 0, 0));
      sphere_pos.push_back(vec3(3, 3, 3)); sphere_col.push_back(vec3(0, 2, 0));

      // add one arrow!
      arrow_head.push_back(0); arrow_tail.push_back(1); arrow_col.push_back(vec3(0, 0, 2));
    }
  }

  float screenX, screenY;
  unsigned int ci = 0;
  for(vector<vec3>::iterator it = sphere_pos.begin(); it != sphere_pos.end(); it++){

    if(ci < csv.size() || ci < (next_label - 33) ){
      // only draw nodes for merges, not individual data elements
      ci ++;
      continue;
    }
    if(myPickNames.size() < 1){
      sphere_col[ci].color();
    }
    else{
      if(myPickNames.count(ci) > 0){
        sphere_col[ci].invert();
        if(ci != last_pick){
          cout << "pick: " << ci << " p_count " << p_count[ci] << endl;
        }
        last_pick = ci;
      }
      else{
        sphere_col[ci].color();
      }
    }
    glPushMatrix();
    vec3 tx(sphere_pos[ci] - rX); // ideally this transform would move out of the loop
    convert_3d_to_2d(tx.x, tx.y, tx.z, screenX, screenY);

    tx.translate();
    if(p_select) glPushName(ci);
    draw_sphere(5. * SPHERE_RADIUS * ((float)p_count[ci]) / ((float)csv.size()));
    if(p_select) glPopName();
    glPopMatrix();

    if(draw_text){
      setOrthographicProjection();
      glPushMatrix();
      glLoadIdentity();
      glColor3f(.9, 0., 0.);
      string ds(str("|") + to_string(ci) + str("|=") + to_string(p_count[ci]));
      renderBitmapString(screenX, -10 -screenY, ds.c_str());
      //renderBitmapString(screenX - 11, -10 - screenY, (str("i=") + std::to_string(ci)).c_str());
      // glColor3f(1., 0., 1.);
      // renderBitmapString(screenX + 31, -10 - screenY, std::to_string(p_count[ci]).c_str());

      glPopMatrix();
      resetPerspectiveProjection();
    }

    ci ++;
    // vector::iterator it = sphere_pos.begin();
  }

  return; //

  // use a hyperbolic coordinate system instead of fbl
  ci = 0;
  for(vector<vec3>::iterator it = arrow_col.begin(); it != arrow_col.end(); it++){

    // sphere centres
    vec3 Mx1(sphere_pos[arrow_head[ci]] - rX);
    vec3 Mx2(sphere_pos[arrow_tail[ci]] - rX);

    vec3 dx(Mx2 - Mx1);
    float len = dx.length();

    // from first sphere centre to outside of second sphere
    dx = dx * ((len - SPHERE_RADIUS) / len); // * dx;
    float tPL = ARROWHEAD_LENGTH;
    vec3 tx(dx - (dx * (tPL / len)));
    vec3 normalV(-dx.y, dx.x, 0.);
    normalV = normalV / normalV.length();
    float tNormal = ARROWHEAD_WIDTH;
    vec3 leftP(tx + ( normalV*tNormal));
    vec3 rightP(tx - ( normalV*tNormal));

    vec3 nV2( tx.cross(normalV));
    nV2 = nV2 / nV2.length();
    vec3 leftP2(tx + ( nV2 * tNormal));
    vec3 rightP2(tx - ( nV2 * tNormal));

    glLineWidth(1.5);
    arrow_col[ci].color();

    glPushMatrix();
    glBegin(GL_LINES); Mx1.vertex(); Mx2.vertex(); glEnd();
    glPopMatrix();

    glPushMatrix();
    glTranslatef(Mx1.x, Mx1.y, Mx1.z);
    glBegin(GL_TRIANGLES); tx.vertex(); leftP.vertex(); dx.vertex(); glEnd();
    glBegin(GL_TRIANGLES); tx.vertex(); rightP.vertex(); dx.vertex(); glEnd();
    glPopMatrix();

    glPushMatrix();
    glTranslatef(Mx1.x, Mx1.y, Mx1.z);
    glBegin(GL_TRIANGLES); tx.vertex(); leftP2.vertex(); dx.vertex(); glEnd();
    glBegin(GL_TRIANGLES); tx.vertex(); rightP2.vertex(); dx.vertex(); glEnd();
    glPopMatrix();
    ci ++;
  }

  if(debug){
    // draw axes
    glPushMatrix();
    glColor3f(1, 0, 0);
    glBegin(GL_LINES);
    glVertex3f(0. - rX.x, 0 - rX.y, 0 - rX.z);
    glVertex3f(1. - rX.x, 0 - rX.y ,0 - rX.z);
    glEnd();
    glPopMatrix();

    glPushMatrix();
    glColor3f(0, 1, 0);
    glBegin(GL_LINES);
    glVertex3f(0. - rX.x, 0. - rX.y, 0 - rX.z);
    glVertex3f(0. - rX.x, 1. - rX.y, 0 - rX.z);
    glEnd();
    glPopMatrix();

    glPushMatrix();
    glColor3f(0, 0, 1);
    glBegin(GL_LINES);
    glVertex3f(0. - rX.x, 0 - rX.y, 0. - rX.z);
    glVertex3f(0. - rX.x, 0 - rX.y, 1. - rX.z);
    glEnd();
    glPopMatrix();
  }
}

GLvoid drawScene(int p_select){
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  draw(p_select);
  glFlush();
  SWAPBUFFERS;
}

void hclust(){
  sphere_pos.clear();
  sphere_col.clear();
  arrow_head.clear();
  arrow_tail.clear();
  arrow_col.clear();

  float R_FACT = 0.; //125.;
  float z = R_FACT * (float)rand() / (float) RAND_MAX;

  vec3 pink(0, 1, 0);
  vec3 antipink(1. - pink.x, 1. - pink.y, 1. - pink.z);
  vec3 line_colour(0., 0., 1.);

  vec3 leaf_colour(antipink);
  vec3 node_colour(pink);

  int debug = false;
  size_t i, j;
  size_t n_records = csv.size();

  size_t my_label;
  next_label = n_records; // progressively inclusive labels will start on new numerological turf
  if(debug) cout << "==============================" << endl;

  if(debug) cout << "next_label " << next_label << " final label should be <= (n^2 - n) / 2 = " << (n_records * n_records - n_records ) / 2 << endl;
  /*
  map<size_t, size_t> meta;
  map<size_t, size_t> up;
  map<size_t, size_t> count;
  */
  // idea: iterative incarnations of recursive or hierarchical things-- conceptual unification of iteration and hierarchy
  // dictionary (non-pointer) implementation of disjoint-set forest

  // seed the "simulation" (bad terminology)
  for0(i, n_records){
    meta[i] = i;//up[i] = i;
    sphere_pos.push_back(vec3(0, (float)i, z)); sphere_col.push_back(leaf_colour);
    z =R_FACT* (float)rand() / (float)RAND_MAX;
    p_count[i] = 1;
  }

  // n.b. in "top" all keys will eventually all map to the same value,
  // whereas label maps to the next most inclusive node (value) AKA set (up arrow)

  size_t iter = 1;
  stack<f_i> tmp;
  while(dmat.size() > 0){
    bool new_label_this_iter = false;

    float x = dmat.top().f;

    map<size_t, size_t> meta_p;
    meta_p.clear();

    if(debug) cout << "meta: " << meta << endl;
    while(dmat.size() > 0 && dmat.top().f == x){
      f_i a(dmat.top());

      size_t a_i = a.i;

      i = a_i / n_records;
      j = a_i % n_records;

      // might need to put this back in
      // cout << "*fij(" << a.f << "," << i << "," << j << ")" << endl;
      if(debug) cout << "pull " << dmat.top().f << " " << j << "," << i << " mj, mi=" << meta[j] << "," << meta[i] << endl;
      dmat.pop();

      // path flattening
      size_t topi = meta[i];
      while(topi != meta[topi]){
        if(debug) cout << "\tflatten: " << topi << "," << meta[topi] << " --> " << meta[topi] << endl;
        topi = meta[topi];
      }
      size_t topj = meta[j];
      while(topj != meta[topj]){
        if(debug) cout << "\tflatten: " << topj << "," << meta[topj] << " --> " << meta[topj] << endl;
        topj = meta[topj];
      }

      if(topi == topj) continue;

      if(meta_p.count(topi) < 1 && meta_p.count(topj) < 1){
        my_label = next_label ++;
        /* meta_p[i] = meta_p[j] = */
        meta_p[topi] = meta_p[topj] = my_label;
        cout << "\tnew_label " << topi << ", " << topj << " --> " << my_label << " d=" << a.f << endl;
        meta_p[my_label] = my_label;
        sphere_pos.push_back(vec3((float)iter, (float)i, z)); sphere_col.push_back(node_colour); //vec3(0., 1.0, .0));
        z = R_FACT * (float)rand() / (float)RAND_MAX;

        //p_count[my_label] = p_count[topi] + p_count[topj];

        new_label_this_iter = true;
      }
      else if(meta_p.count(topi) < 1){
        meta_p[topi] = meta_p[topj]; cout << "\t" << topi << " --> " << meta_p[topj] << endl;
      }
      else if(meta_p.count(topj) < 1){
        meta_p[topj] = meta_p[topi]; cout << "\t" << topj << " --> " << meta_p[topi] << endl;
      }
      else{
        if(meta_p[topi] == meta_p[topj]){
          if(debug) cout << "\tpass: " << meta_p[topi] << " " << meta_p[topj] << endl;
        }
        else{
          if(debug) cout << "\trela: " << meta_p[topi] << " " << meta_p[topj] << " --> " << max(meta_p[topi], meta_p[topj]) << endl;
          meta_p[topi] = meta_p[topj] = max(meta_p[topi], meta_p[topj]);
        }
      }

    }
    if(debug) cout << "relabel: " << endl;
    for(map<size_t, size_t>::iterator it = meta_p.begin(); it != meta_p.end(); it ++){
      meta[it->first] = it->second;
      // cout << "\t" << it->first << " --> " << it->second << endl;

      if(it->first != it->second){
        p_count[it->second] += p_count[it->first];
        cout << "\t*" << it->first << " --> " << it->second << endl;
        arrow_head.push_back(it->first);
        arrow_tail.push_back(it->second);
        arrow_col.push_back(line_colour);
      }
    }

    if(debug) cout <<"*eta: " << meta << endl;
    iter += 1;

    if(new_label_this_iter) cout << endl /*<< iter*/ << "------------------------------" << endl;
  }
}

void read_data(str fn){
  size_t ci = 0; // row count

  // open the input data
  ifstream g(fn);
  if(!g.is_open()) err("failed to opend input file");
  string s;

  // read header
  getline(g, hdr);
  while(getline(g, s)){
    csv.push_back(s);
    ci ++;
  }
  g.close();
  cout << "fields: " << split(hdr) << endl;
  cout << "rcords: " << csv.size() << endl; // first record is header
  // n.b. need to project that onto the data
}

float * dmat_d;
size_t * dmat_i;

void read_dmat(){
  // allocate memory
  size_t n_records = csv.size();
  size_t k_max = fsize("dmat.d") / (sizeof(float) * n_records);
  cout << "kmax " << k_max << endl;

  if(dmat_d == NULL){
    dmat_d = (float *) alloc(n_records * k_max * sizeof(float));
  }
  if(dmat_i == NULL){
    dmat_i = (size_t *) alloc(n_records * k_max * sizeof(size_t));
  }

  if(true){
    // read truncated sorted distance-matrix
    FILE * f;
    f = fopen("dmat.d", "rb");
    cout << " read " << n_records * k_max * sizeof(float) << endl;
    size_t fr = fread(dmat_d, n_records * k_max * sizeof(float), 1, f);
    if(fr != 1) err("read fail 1");
    fclose(f);

    f = fopen("dmat.i", "rb");
    cout << " read " << n_records * k_max * sizeof(size_t) << endl;
    fr = fread(dmat_i, n_records * k_max * sizeof(size_t), 1, f);
    if(fr != 1) err("read fail 2");
    fclose(f);
  }

  size_t u, i, j, k;

  for(u = 0; u < (n_records * k_max); u++){
    float f = dmat_d[u];
    i = u / k_max;
    j = dmat_i[u];
    size_t ki = i * n_records + j;
    f_i a(f, ki);
    // might need to put this one back in:
    // printf("f %f i %ld j %ld ki %ld u %ld\n", f, (long int)i, (long int)j, (long int)ki, (long int)u);
    dmat.push(a);
  }
}

void cluster(){
  str fn(data_files[cur_data_file]);
  strip(fn);
  cout << "filename: " << fn << endl;

  cout << "read data.." << endl;
  read_data(fn); // read the data

  read_dmat();

  cout << "hclust.." << endl;
  hclust(); // hierarchical clustering upon: truncated sorted distance matrix

}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow){
  dmat_d = (float *) NULL;
  dmat_i = (size_t *) NULL;

  data = NULL;
  cur_data_file = 0; // start with the first file
  str fn("");
  str fns("");

  /* check to see if we can get the input data */
  ifstream f("./.vis");
  if(!f.is_open()) err("failed to open input file: .vis");

  std::getline(f, fns);
  data_files = split(fns);
  cout << "data files: " << data_files << endl;
  fn = data_files[0];
  cout << "fn: " << fn << endl;
  f.close();

  cluster();

  rX.zero();
  myZFar = 10.;
  myZNear = -10.;
  SHIFT_KEY = false;
  last_pick = -1;
  _mouseLeft = _mouseRight = false;
  _dragPosX = _dragPosY = _dragPosZ = 0.0;
  myLeft = myRight = myBottom = myTop = 0.;
  for(int i = 0; i < 4; i++) zprReferencePoint[i] = 0.;
  _mouseX = _mouseY = _mouseLeft = _mouseMiddle = _mouseRight = 0;

  set_width(1440);
  set_height(1440);
  zprReferencePoint[0] = zprReferencePoint[1] = zprReferencePoint[2] = zprReferencePoint[3] = 0.;
  getMatrix();

  MSG msg;
  WNDCLASS wndclass;

  /* Register the frame class */
  wndclass.lpfnWndProc = (WNDPROC)MainWndProc;
  wndclass.style = wndclass.cbClsExtra = wndclass.cbWndExtra = 0;
  wndclass.hInstance = hInstance;
  wndclass.hIcon = LoadIcon (hInstance, window_name);
  wndclass.hCursor = LoadCursor (NULL,IDC_ARROW);
  wndclass.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
  wndclass.lpszMenuName = wndclass.lpszClassName = window_name;

  if(!RegisterClass(&wndclass)) return FALSE;

  /* Create the frame */
  ghWnd = CreateWindow (window_name, "OpenGL: shift-click to re-centre, ctrl to drag", WS_OVERLAPPEDWINDOW | WS_CLIPSIBLINGS | WS_CLIPCHILDREN, CW_USEDEFAULT, CW_USEDEFAULT, WIDTH, HEIGHT, NULL, NULL, hInstance, NULL);
  if (!ghWnd) return FALSE; // confirm window created
  ShowWindow (ghWnd, nCmdShow); // show and update main window
  UpdateWindow (ghWnd);

  /* animation loop */
  while(1){
    while(PeekMessage(&msg, NULL, 0, 0, PM_NOREMOVE) == TRUE){
      if(GetMessage(&msg, NULL, 0, 0)){
        TranslateMessage(&msg);
        DispatchMessage(&msg);
      }
      else return TRUE;
    }
    drawScene(false);
  }
}
