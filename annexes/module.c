@module A
{
  int	i = 0;
  
  void 	f();
  int  	f(char, float);
}

// Si le fichier est un ".kh"
#ifndef FICHIER_PARSE_H
#define FICHIER_PARSE_H

int	Var$A$i$$int = 0;
void	Func$A$f$$void();
int	Func$A$f$$int$$char$$float(char, float);

#endif
