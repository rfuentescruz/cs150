move(1, 6).
move(1, 8).
move(2, 7).
move(2, 9).
move(3, 4).
move(3, 8).
move(4, 9).
move(6, 7).

moves(X, Y) :-
  move(X, Y);
  move(Y, X).

path(X, Y) :-
  path(X, Y, L),
  printSolution(L).

path(X, Y, [X, Y]) :- moves(X, Y).
path(X, Z, [X | L]) :- path(Y, Z, L), moves(X, Y), not(member(X, L)).

printSolution([]).
printSolution([H | T]) :- write(H), nl, printSolution(T).
