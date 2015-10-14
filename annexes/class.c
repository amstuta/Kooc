@class A
{
  char c = '0';
  @member int i;
  @virtual void get_void();
}

@class B : A
{
  @virtual void get_void();
}

typedef struct _kc_A	A;
typedef struct _kc_vt_A	vt_A;

struct _kc_A
{
  Object parent;
  int Var$A$i$$int;
};

struct _kc_vt_A
{
  // Champs de la Vtable parent (Object)
  void (*clean$P$void)(Object *);
  int (*isKindOf$P$int)(Object *, const char *);
  int (*isKindOf2$P$int)(Object *, Object *);
  int (*isInstanceOf$P$int)(Object *, const char *);
  int (*isInstanceOf2$P$int)(Object *, Object *);

  // Champs ajoutés
  void (*get_void$P$void)(A*);
};

char Var$A$c$char = '0';
vt_A vtable_A = { &Func$Object$clean$$void$P$Object, &Func$Object$isKindOf$$int$P$Object$P$char, &Func$Object$isKindOf$$int$P$Object$P$Object, &Func$Object$isInstanceOf$$int$P$Object$P$char, &Func$Object$isInstanceOf$$int$P$Object$P$Object, &Func$A$get_void$$void$P$A };


typedef struct _kc_B	B;
typedef struct _kc_vt_B	vt_B;

struct _kc_B
{
  A parent;
};

struct _kc_vt_B
{
  // Champs de la Vtable parent (A)
  void (*clean$P$void)(Object *);
  int (*isKindOf$P$int)(Object *, const char *);
  int (*isKindOf2$P$int)(Object *, Object *);
  int (*isInstanceOf$P$int)(Object *, const char *);
  int (*isInstanceOf2$P$int)(Object *, Object *);
  void (*get_void$P$void)(A*);
};

vt_B vtable_B = { &Func$Object$clean$$void$P$Object, &Func$Object$isKindOf$$int$P$Object$P$char, &Func$Object$isKindOf$$int$P$Object$P$Object, &Func$Object$isInstanceOf$$int$P$Object$P$char, &Func$Object$isInstanceOf$$int$P$Object$P$Object, &Func$B$get_void$$void$P$B };
