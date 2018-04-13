simpsons :: (Floating a) => (a -> a) -> a -> a -> a
simpsons f a b = ((b - a) / 6) * (f(a) + (4 * f((a + b) / 2)) + f(b))

trapezoidal :: (Floating a) => (a -> a) -> a -> a -> a
trapezoidal f a b = (b - a) * ((f(a) + f(b)) / 2)

factorial :: (Integral a) => a -> a
factorial n = foldl (*) 1 [1..n]

term :: (Floating a, Integral b) => a -> b -> a
term x y = (x ^^ y) / fromIntegral(factorial y)

series :: (Floating a) => a -> [a]
series x = [sign * (term x exp) | (exp, sign) <- zip [1,3..] (cycle [1, -1])]

sin' :: (Floating a) => a -> a
sin' x = foldl (+) 0 (take 30 (series x))
