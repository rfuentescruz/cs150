-- | Approximate a function f(x) using Simpson's Rule
simpsons :: (Floating a) => (a -> a) -> a -> a -> a
simpsons f a b = ((b - a) / 6) * (f(a) + (4 * f((a + b) / 2)) + f(b))

-- | Approximate a function f(x) using the Trapezoidal Rule
trapezoidal :: (Floating a) => (a -> a) -> a -> a -> a
trapezoidal f a b = (b - a) * ((f(a) + f(b)) / 2)

-- | Approximate sin(x) using 30 terms of its Maclaurin series using foldl
sin_foldl :: (Floating a) => a -> a
sin_foldl x = foldl (+) 0 (take 30 (series x))

-- | Approximate sin(x) by recursively computing the sum of its Maclaurin series
sin_recursive :: (Floating a, Ord a) => a -> a -> a
sin_recursive x tolerance = maclaurin (series x) tolerance

--------------------------- MISC FUNCTIONS ---------------------------

-- | Compute the factorial of n
factorial :: (Integral a) => a -> a
factorial n = foldl (*) 1 [1..n]

-- | Generate a term of the Maclaurin series for sin(x)
term :: (Floating a, Integral b) => a -> b -> a
term x y = (x ^^ y) / fromIntegral(factorial y)

-- | Generate the Maclaurin series for sin(x)
series :: (Floating a) => a -> [a]
series x = zipWith (*) ([term x exp | exp <- [1,3..]]) (cycle [1, -1])

-- | Recursively compute the sum of an infinite series until the difference
-- |   between the last two terms are below the threshold
maclaurin :: (Floating a, Ord a) => [a] -> a -> a
maclaurin [] _ = 0
maclaurin [n] _ = n
maclaurin (x:xs) threshold
    | diff > threshold = x + (maclaurin xs threshold)
    | otherwise        = x
    where diff = abs (x - head xs)

-- | f(x) = 2x^2 + 5x + 12
test :: (Num a) => a -> a
test x = (2 * x ^ 2) + (5 * x) + 12

--------------------------- MAIN ---------------------------
main = do
  print(simpsons test 1 3)
  print(trapezoidal test 1 3)
  print(sin_foldl (3 * pi / 2))
  print(sin_recursive (pi / 2) 0.0000000000000000001)
