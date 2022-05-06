//  Copyright 2019 Province of British Columbia
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

/* g++ graphics.cpp -lopengl32 -lglu32 -lgdi32
test opengl graphics without any extra drivers or libraries */
#include<set>
#include<stack>
#include"misc.h"
#include<vector>
#include<math.h>
#include<cfloat>
#include<GL/gl.h>
#include<fstream>
#include<iostream>
#include<GL/glu.h>
#include<stdlib.h>
#include<windows.h>
#include<pthread.h>
using namespace std;

// clustering stuff
void cluster();
int cur_data_file;
vector<str> data_files;
size_t next_label;

// visualization stuff
int last_pick;
vector<str> captions; // sphere labels

// stuff for distance-matrix calculation
str hdr; // csv fields
vector<str> csv; // comma-separated input data
str * data;

/* Windows globals, defines, and prototypes */
HDC ghDC;
HGLRC ghRC;
HWND ghWnd;
CHAR window_name[]="glut";

#define SWAPBUFFERS SwapBuffers(ghDC)
#define MAXBUFFERSIZE 1024

#define SPHERE_RADIUS 0.015 // this needs to be dynamic with the size of the stuff
#define ARROWHEAD_LENGTH (0.25 * SPHERE_RADIUS)
#define ARROWHEAD_WIDTH (0.175 * SPHERE_RADIUS)

class vec3{
  public:
  float x, y, z;
  vec3( float xx, float yy, float zz){
    x = xx; y = yy; z = zz;
  }
  vec3(){
  }
  void init(float X, float Y, float Z){
    x=X; y=Y; z=Z;
  }
  void init(vec3 & a){
    x=a.x; y=a.y; z=a.z;
  }

  vec3(const vec3 & other){
    x = other.x; y = other.y; z = other.z;
  }
  vec3 & operator=( vec3 & rhs ){
    x = rhs.x; y = rhs.y; z = rhs.z;
  }
  float dot( vec3 & other){
    return x*other.x + y*other.y + z*other.z;
  }
  vec3 & cross( vec3 & other){
    vec3 * ret = new vec3();
    ret->x = y * other.z - z * other.y;
    ret->y = z * other.x - x * other.z;
    ret->z = x * other.y - y * other.x;
    return *ret;
  }
  int operator==(vec3 rhs){
    return ( x==rhs.x && y==rhs.y && z == rhs.z);
  }
  vec3 & operator+(vec3 rhs){
    vec3 * ret = new vec3(x + rhs.x, y+rhs.y, z+rhs.z);
    return *ret;
  }
  vec3 operator-(vec3 rhs){
    vec3* ret = new vec3( x-rhs.x, y-rhs.y, z-rhs.z);
    return *ret;
  }
  vec3 & operator+(float s){
    vec3* ret = new vec3( x+s,y+s,z+s);
    return *ret;
  }
  vec3 & operator-(float s){
    vec3* ret = new vec3( x-s,y-s,z-s);
    return *ret;
  }
  vec3 & operator*(float s){
    vec3* ret = new vec3( x*s, y*s, z*s);
    return *ret;
  }
  vec3 & operator/(float s){
    vec3* ret = new vec3( x/s, y/s ,z/s);
    return *ret;
  }
  vec3 &operator +=(vec3 rhs){
    x += rhs.x;
    y += rhs.y;
    z += rhs.z;
  }
  vec3 &operator -=(vec3 rhs){
    x -= rhs.x;
    y -= rhs.y;
    z -= rhs.z;
  }

  float length(){
    return sqrt( x*x +y*y +z*z);
  }
  inline void vertex(){
    glVertex3f( x, y, z);
  }
  inline void color(){
    glColor3f(x, y, z);
  }
  inline void invert(){
    glColor3f(1. - x, 1. - y, 1. - z);
  }
  inline void translate(){
    glTranslatef(x, y, z);
  }
  inline void zero(){
    x = y = z = 0.;
  }
};

vec3 rX; // relative position variable: 3d reference point for shifting perspetive
void draw_sphere(GLfloat _radius){
  const float GL_PI = 3.141592;
  GLfloat alpha, beta, x, y, z; // Storage for coordinates and angles
    int gradation = 3;

  for (alpha = 0.0; alpha < GL_PI; alpha += GL_PI/gradation){
    glBegin(GL_TRIANGLE_STRIP);
    for (beta = 0.0; beta < 2.01*GL_PI; beta += GL_PI/gradation){
      //glBegin(GL_LINES);
      x = _radius*cos(beta)*sin(alpha);
      y = _radius*sin(beta)*sin(alpha);
      z = _radius*cos(alpha);
      glVertex3f(x, y, z);
      x = _radius*cos(beta)*sin(alpha + GL_PI/gradation);
      y = _radius*sin(beta)*sin(alpha + GL_PI/gradation);
      z = _radius*cos(alpha + GL_PI/gradation);
      glVertex3f(x, y, z);
      // glEnd();
    }
    glEnd();
  }
}

// variables for clustering vis ------------------------------
vector<vec3> sphere_pos;
vector<vec3> sphere_col;
std::set<GLint> myPickNames;

vector<unsigned int> arrow_head;
vector<unsigned int> arrow_tail;
vector<vec3> arrow_col;
// -----------------------------------------------------------

int SHIFT_KEY;
int CONTROL_KEY;

// int rMouseX, rMouseY; // 20190712 added to compensate for an annoying effect
float myLeft, myRight, myBottom, myTop, myZNear, myZFar;
int _mouseX,_mouseY, _mouseLeft, _mouseMiddle, _mouseRight;
double _left,_right, _top,_bottom,_near,_far,_zNear,_zFar, _dragPosX, _dragPosY, _dragPosZ;
double _matrix[16];
double _matrixInverse[16];
GLfloat zprReferencePoint[4];

static unsigned int WIDTH;
static unsigned int HEIGHT;
void set_width(unsigned int w){
  WIDTH = w;
}
void set_height(unsigned int h){
  HEIGHT = h;
}

LONG WINAPI MainWndProc(HWND, UINT, WPARAM, LPARAM);
BOOL bSetupPixelFormat(HDC);

/* OpenGL globals, defines, and prototypes */
GLfloat latitude, longitude, latinc, longinc;
GLdouble radius;

GLvoid resize(GLsizei, GLsizei);
GLvoid initializeGL(GLsizei, GLsizei);
GLvoid drawScene(int p_select); //GLvoid);
void polarView(GLdouble, GLdouble, GLdouble, GLdouble);

BOOL bSetupPixelFormat(HDC hdc){
  PIXELFORMATDESCRIPTOR pfd = {
    sizeof(PIXELFORMATDESCRIPTOR), // size of this pfd
    1, // version number
    PFD_DRAW_TO_WINDOW | // support window
    PFD_SUPPORT_OPENGL | // support OpenGL
    PFD_DOUBLEBUFFER, // double buffered
    PFD_TYPE_RGBA, // RGBA type
    24, // 24-bit color depth
    0, 0, 0, 0, 0, 0, // color bits ignored
    0, // no alpha buffer
    0, // shift bit ignored
    0, // no accumulation buffer
    0, 0, 0, 0, // accum bits ignored
    32, // 32-bit z-buffer
    0, // no stencil buffer
    0, // no auxiliary buffer
    PFD_MAIN_PLANE, // main layer
    0, // reserved
    0, 0, 0 // layer masks ignored
  };

  int pixelformat;
  pixelformat = ChoosePixelFormat(hdc, &pfd);
  if(pixelformat ==0){
    MessageBox(NULL, "ChoosePixelFormat failed", "Error", MB_OK);
    return FALSE;
  }
  if(SetPixelFormat(hdc, pixelformat, &pfd) == FALSE){
    MessageBox(NULL, "SetPixelFormat failed", "Error", MB_OK);
    return FALSE;
  }
  return TRUE;
}

void invertMatrix(const GLdouble *m, GLdouble *out );
void getMatrix();
void processHits(GLint hits, GLuint buffer[]);
void zprPick(GLdouble x, GLdouble y,GLdouble delX, GLdouble delY);

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow);

void setOrthographicProjection() {
  int h = HEIGHT;
  int w = WIDTH;
  glMatrixMode(GL_PROJECTION);
  glPushMatrix();
  glLoadIdentity();
  gluOrtho2D(0., (float)w, 0., (float)h);
  glScalef(1., -1., 1.);
  glTranslatef(0., -1. * (float)h, 0.);
  glMatrixMode(GL_MODELVIEW);
}

void resetPerspectiveProjection(){
  glMatrixMode(GL_PROJECTION);
  glPopMatrix();
  glMatrixMode(GL_MODELVIEW);
}

void pos(double *px, double *py, double *pz, const int x, const int y, const int *viewport){
  /*
  * Use the ortho projection and viewport information
  * to map from mouse co-ordinates back into world
  * co-ordinates
  * */
  *px = (double)(x - viewport[0]) / (double)(viewport[2]);
  *py = (double)(y - viewport[1]) / (double)(viewport[3]);

  *px = _left + (*px) * (_right-_left);
  *py = _top + (*py) * (_bottom-_top);
  *pz = _zNear;
}

double vlen(double x,double y,double z){
  return sqrt(x * x + y * y + z * z);
}

GLvoid draw(int p_select);

void zprMotion(GLint x, GLint y){
  bool changed = false;
  int dx = x - _mouseX;
  int dy = y - _mouseY;
  if(dx == 0 and dy == 0){
    return;
  }

  GLint viewport[4];
  glGetIntegerv(GL_VIEWPORT,viewport);
  double px,py,pz;
  pos(&px, &py, &pz, x, y, viewport);

  if(CONTROL_KEY && _mouseLeft){
    if(myPickNames.size() == 1){
      set<GLint>::iterator it = myPickNames.begin();
      vec3 * a = &sphere_pos[*it]; // sphere centre coord, for name *it
      GLdouble proj[16]; // vars
      GLdouble model[16];
      GLint view[4];
      GLdouble nearx,neary,nearz;

      // proj., model, view mats
      glGetDoublev(GL_PROJECTION_MATRIX,proj);
      glGetDoublev(GL_MODELVIEW_MATRIX,model);
      glGetIntegerv(GL_VIEWPORT,view);

      float screendx = (float)x - (float)_mouseX;
      float screendy = (float)y - (float)_mouseY;
      double mx, my, mz, vx, vy, vz;
      mx = (double) a->x;
      my = (double) a->y;
      mz = (double) a->z;

      //world xyz onto screen xyz
      gluProject(mx, my, mz, model, proj, view, &vx, &vy, &vz);

      float screeny = vy - screendy;
      float screenx = vx + screendx;

      //screen xyz onto world xyz
      gluUnProject(screenx, screeny, vz, model,proj,view,&nearx,&neary,&nearz);
      vec3 newa((float)nearx - mx, (float)neary -my, (float)nearz-mz);
      vec3 translation(a->x + newa.x, a->y + newa.y, a->z + newa.z);
      a->x = translation.x;
      a->y = translation.y;
      a->z = translation.z;

      draw(false);
      //SWAPBUFFERS; a->Update = true; glutPostRedisplay(); display(); glutSwapBuffers();
      _dragPosX = px;
      _dragPosY = py;
      _dragPosZ = pz;
      _mouseX = x;
      _mouseY = y;
      changed = true;
    }
  }
  else{
    if(myPickNames.size() < 1){
      if(_mouseLeft && _mouseRight){
        // zoom
        double s = exp((double)dy*0.01);
        glTranslatef( zprReferencePoint[0], zprReferencePoint[1], zprReferencePoint[2]);
        glScalef(s,s,s);
        glTranslatef(-zprReferencePoint[0],-zprReferencePoint[1],-zprReferencePoint[2]);
        changed = true;
      }
      else if(_mouseRight){
        // pan
        if(true){
          glMatrixMode(GL_MODELVIEW);
          glLoadIdentity();
          glTranslatef(px-_dragPosX,py-_dragPosY,pz-_dragPosZ);
          glMultMatrixd(_matrix);
          _dragPosX = px;
          _dragPosY = py;
          _dragPosZ = pz;
          changed = true;
        }
      }
      else if(_mouseLeft){
        // rotate
        double ax, ay, az, bx, by, bz, angle;
        ax = dy;
        ay = dx;
        az = 0.0;
        angle = vlen(ax,ay,az)/(double)(viewport[2]+1)*180.0;
        /* Use inverse matrix to determine local axis of rotation */
        bx = _matrixInverse[0]*ax + _matrixInverse[4]*ay + _matrixInverse[8] *az;
        by = _matrixInverse[1]*ax + _matrixInverse[5]*ay + _matrixInverse[9] *az;
        bz = _matrixInverse[2]*ax + _matrixInverse[6]*ay + _matrixInverse[10]*az;
        glTranslatef( zprReferencePoint[0], zprReferencePoint[1], zprReferencePoint[2]);
        glRotatef(angle,bx,by,bz);
        glTranslatef(-zprReferencePoint[0],-zprReferencePoint[1],-zprReferencePoint[2]);
        changed = true;
      }
      _mouseX = x;
      _mouseY = y;
    }
  }
  if(changed){
    getMatrix();
    //SWAPBUFFERS; glutPostRedisplay();
  }
}

void getMatrix(){
  glGetDoublev(GL_MODELVIEW_MATRIX,_matrix);
  invertMatrix(_matrix,_matrixInverse);
}

void invertMatrix(const GLdouble *m, GLdouble *out){
  #define MAT(m,r,c) (m)[(c)*4+(r)]
  #define m11 MAT(m,0,0)
  #define m12 MAT(m,0,1)
  #define m13 MAT(m,0,2)
  #define m14 MAT(m,0,3)
  #define m21 MAT(m,1,0)
  #define m22 MAT(m,1,1)
  #define m23 MAT(m,1,2)
  #define m24 MAT(m,1,3)
  #define m31 MAT(m,2,0)
  #define m32 MAT(m,2,1)
  #define m33 MAT(m,2,2)
  #define m34 MAT(m,2,3)
  #define m41 MAT(m,3,0)
  #define m42 MAT(m,3,1)
  #define m43 MAT(m,3,2)
  #define m44 MAT(m,3,3)

  GLdouble det;
  GLdouble d12, d13, d23, d24, d34, d41;
  GLdouble tmp[16];

  d12 = (m31*m42-m41*m32);
  d13 = (m31*m43-m41*m33);
  d23 = (m32*m43-m42*m33);
  d24 = (m32*m44-m42*m34);
  d34 = (m33*m44-m43*m34);
  d41 = (m34*m41-m44*m31);

  tmp[0] = (m22 * d34 - m23 * d24 + m24 * d23);
  tmp[1] = -(m21 * d34 + m23 * d41 + m24 * d13);
  tmp[2] = (m21 * d24 + m22 * d41 + m24 * d12);
  tmp[3] = -(m21 * d23 - m22 * d13 + m23 * d12);

  det = m11 * tmp[0] + m12 * tmp[1] + m13 * tmp[2] + m14 * tmp[3];
  if(det != 0){
    GLdouble invDet = 1.0 / det;

    tmp[0] *= invDet;
    tmp[1] *= invDet;
    tmp[2] *= invDet;
    tmp[3] *= invDet;

    tmp[4] = -(m12 * d34 - m13 * d24 + m14 * d23) * invDet;
    tmp[5] = (m11 * d34 + m13 * d41 + m14 * d13) * invDet;
    tmp[6] = -(m11 * d24 + m12 * d41 + m14 * d12) * invDet;
    tmp[7] = (m11 * d23 - m12 * d13 + m13 * d12) * invDet;

    /* Pre-compute 2x2 dets for first two rows when computing */
    /* cofactors of last two rows. */
    d12 = m11*m22-m21*m12;
    d13 = m11*m23-m21*m13;
    d23 = m12*m23-m22*m13;
    d24 = m12*m24-m22*m14;
    d34 = m13*m24-m23*m14;
    d41 = m14*m21-m24*m11;

    tmp[8] = (m42 * d34 - m43 * d24 + m44 * d23) * invDet;
    tmp[9] = -(m41 * d34 + m43 * d41 + m44 * d13) * invDet;
    tmp[10] = (m41 * d24 + m42 * d41 + m44 * d12) * invDet;
    tmp[11] = -(m41 * d23 - m42 * d13 + m43 * d12) * invDet;
    tmp[12] = -(m32 * d34 - m33 * d24 + m34 * d23) * invDet;
    tmp[13] = (m31 * d34 + m33 * d41 + m34 * d13) * invDet;
    tmp[14] = -(m31 * d24 + m32 * d41 + m34 * d12) * invDet;
    tmp[15] = (m31 * d23 - m32 * d13 + m33 * d12) * invDet;

    memcpy(out, tmp, 16*sizeof(GLdouble));

  }
  #undef m11
  #undef m12
  #undef m13
  #undef m14
  #undef m21
  #undef m22
  #undef m23
  #undef m24
  #undef m31
  #undef m32
  #undef m33
  #undef m34
  #undef m41
  #undef m42
  #undef m43
  #undef m44
  #undef MAT
}

void glut_keyboard_func(GLint wParam);

GLint mouseX, mouseY;

/* main window procedure */
LONG WINAPI MainWndProc(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam){
  RECT rect;
  LONG lRet = 1;
  PAINTSTRUCT ps;
  GLint mouseX, mouseY;

  mouseX = LOWORD(lParam);
  mouseY = HIWORD(lParam);

  switch(uMsg){
    case WM_CREATE:
    ghDC = GetDC(hWnd);
    if (!bSetupPixelFormat(ghDC))
    PostQuitMessage(0);

    ghRC = wglCreateContext(ghDC);
    wglMakeCurrent(ghDC, ghRC);
    GetClientRect(hWnd, &rect);
    initializeGL(rect.right, rect.bottom);
    break;

    case WM_PAINT:
    BeginPaint(hWnd, &ps);
    EndPaint(hWnd, &ps);
    break;

    case WM_SIZE:
    if(true){
      GetClientRect(hWnd, &rect);
      resize(rect.right, rect.bottom);
      WIDTH = rect.right;
      HEIGHT =rect.bottom;

      cout << " WIDTH " << WIDTH << " HEIGHT " << HEIGHT << endl;
    }
    break;

    case WM_CLOSE:
    if (ghRC) wglDeleteContext(ghRC);
    if (ghDC) ReleaseDC(hWnd, ghDC);
    ghRC = 0;
    ghDC = 0;
    DestroyWindow (hWnd);
    break;

    case WM_DESTROY:
    if (ghRC) wglDeleteContext(ghRC);
    if (ghDC) ReleaseDC(hWnd, ghDC);
    PostQuitMessage(0);
    break;

    case WM_KEYDOWN:{
      switch (wParam) {
        case VK_SHIFT: SHIFT_KEY = true; break;
        case VK_CONTROL: CONTROL_KEY = true; break;
        case VK_LEFT:
        if(cur_data_file > 0){
          cur_data_file -= 1;
          cout << "cur_data_file --" << endl;
          cluster();
        }
        else{
          cout << "cur_data_file " << cur_data_file << endl;
        }
        break;
        case VK_RIGHT:
        if(cur_data_file < data_files.size() - 1){
          cur_data_file += 1;
          cout << "cur_data_file ++" << endl;
          cluster();
        }
        else{
          cout << "cur_data_file " << cur_data_file << endl;
        }

        break;
        case VK_UP: break;
        case VK_DOWN: break;
        case VK_ESCAPE: exit(1);
      }
    }

    cout <<"key press: " << wParam << endl;
    break;

    case WM_KEYUP:
    if(true){
      switch (wParam) {
        case VK_SHIFT: SHIFT_KEY = false; break;
        case VK_CONTROL: CONTROL_KEY = false; break;
        case VK_LEFT: break;
        case VK_RIGHT: break;
        case VK_UP: break;
        case VK_DOWN: break;
        case VK_ESCAPE: exit(1);
      }
    }

    break;

    case WM_LBUTTONDOWN:
    if(true){
      _mouseLeft = true;
      mouseX = LOWORD(lParam);
      mouseY = HIWORD(lParam);
      GLint x = mouseX;
      GLint y = mouseY;
      GLint viewport[4];
      zprPick(mouseX, HEIGHT - 1 - mouseY, 3, 3);
      glGetIntegerv(GL_VIEWPORT, viewport);
      pos(&_dragPosX, &_dragPosY, &_dragPosZ, x, y, viewport);
      _mouseX = mouseX;
      _mouseY = mouseY;
    }
    break;

    case WM_RBUTTONDOWN:
    if(true){
      _mouseRight = true;
      mouseX = LOWORD(lParam);
      mouseY = HIWORD(lParam);
      GLint x = mouseX;
      GLint y = mouseY;
      GLint viewport[4];
      glGetIntegerv(GL_VIEWPORT,viewport);
      pos(&_dragPosX,&_dragPosY,&_dragPosZ,x,y,viewport);
    }
    break;

    case WM_LBUTTONUP:
    if(true){
      _mouseLeft = false;
      mouseX = LOWORD(lParam);
      mouseY = HIWORD(lParam);
      myPickNames.clear();
    }
    break;

    case WM_RBUTTONUP:
    if(true){
      _mouseRight = false;
      mouseX = LOWORD(lParam);
      mouseY = HIWORD(lParam);
    }
    break;

    case WM_MOUSEMOVE:
    if(true){
      mouseX = LOWORD(lParam);
      mouseY = HIWORD(lParam);
      zprMotion(mouseX, mouseY);
    }
    break;

    case WM_MOUSEWHEEL:
    break;

    default:
    lRet = DefWindowProc (hWnd, uMsg, wParam, lParam);
    break;
  }

  return lRet;
}

void reset_view(){
  rX.init(0., 0., 0.);
  _mouseX = _mouseY = 0;
  _mouseLeft = _mouseMiddle = _mouseRight = 0;
  _dragPosX = _dragPosY = _dragPosZ = 0.0;
  zprReferencePoint[0] = zprReferencePoint[1] = zprReferencePoint[2] = zprReferencePoint[3] = 0.;
  getMatrix();
}

void processHits(GLint hits, GLuint buffer[]){
  unsigned int i, j;
  myPickNames.clear();
  GLuint names, *ptr, minZ, *ptrNames, numberOfNames;
  if(hits <= 0) return;
  //printf ("hits = %d names:{", hits);
  ptr = (GLuint *) buffer;
  minZ = 0xffffffff;
  for0(i, hits){
    //printf("(i%d)",i);
    names = *ptr;
    ptr++;
    GLint mindepth = *ptr; ptr++;
    GLint maxdepth = *ptr; ptr++;
    for0(j, names){
      GLint name = *ptr;
      // printf(",%d",name);
      if(name >= 0){
        myPickNames.insert(name);
        if(SHIFT_KEY){
          rX = sphere_pos[name];
        }
      }
      ptr++;
    }
  }
}

GLvoid draw(int p_select);

void zprPick(GLdouble x, GLdouble y,GLdouble delX, GLdouble delY){
  GLuint buffer[MAXBUFFERSIZE];
  const int bufferSize = sizeof(buffer)/sizeof(GLuint);

  GLint viewport[4];
  GLdouble projection[16];

  GLint hits;
  GLint i,j,k;

  GLint min = -1;
  GLuint minZ = -1;

  glSelectBuffer(bufferSize,buffer); /* Selection buffer for hit records */
  glRenderMode(GL_SELECT); /* OpenGL selection mode */
  glInitNames();
  glMatrixMode(GL_PROJECTION);
  glPushMatrix(); /* Push current projection matrix */
  glGetIntegerv(GL_VIEWPORT,viewport); /* Get the current viewport size */
  glGetDoublev(GL_PROJECTION_MATRIX,projection); /* Get the projection matrix */
  glLoadIdentity(); /* Reset the projection matrix */
  gluPickMatrix(x,y,delX,delY,viewport); /* Set the picking matrix */
  glMultMatrixd(projection); /* Apply projection matrix */

  glMatrixMode(GL_MODELVIEW);
  draw(true);

  // Draw the scene in selection mode
  hits = glRenderMode(GL_RENDER); /* Return to normal rendering mode */
  processHits( hits, buffer);
  glMatrixMode(GL_PROJECTION);
  glPopMatrix(); /* Restore projection matrix */
  glMatrixMode(GL_MODELVIEW);
  return;
}

void convert_3d_to_2d(float x, float y, float z, float & u, float & v){
  GLdouble proj[16]; GLdouble model[16]; GLint view[4];
  glGetDoublev(GL_PROJECTION_MATRIX, proj);
  glGetDoublev(GL_MODELVIEW_MATRIX, model);
  glGetIntegerv(GL_VIEWPORT, view);

  double vx, vy, vz;
  gluProject(x, y, z, model, proj, view, &vx, &vy, &vz);
  u = (float)vx;
  v = (float)(vy - WIDTH);
}
