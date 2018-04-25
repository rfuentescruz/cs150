gcd(X, 0, X).

gcd(M, N, X) :-
  N =\= 0,
  Y is mod(M, N),
  gcd(N, Y, X).
