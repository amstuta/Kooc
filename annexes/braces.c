int i = [A.c];		// Appel à la variable statique 'c' de la classe A
[A f :12];		// Appel de la fonction 'f' de la classe/module A
A *object = [A new];	// Création d'un nouvel objet A
[object.get_void];	// Appel de la fonction virtuelle 'get_void'

int i = Var$A$c$char;
Func$A$f$$void$$int(12);
A* object = Func$A$new$P$A$$void();
((Object*)object)->vt->get_void$P$void(object);
