simpsons :: (Floating a) => (a -> a) -> a -> a -> a
simpsons f a b = ((b - a) / 6) * (f(a) + (4 * f((a + b) / 2)) + f(b))

trapezoidal :: (Floating a) => (a -> a) -> a -> a -> a
trapezoidal f a b = (b - a) * ((f(a) + f(b)) / 2)

factorial :: (Integral a) => a -> a
factorial n = foldl (*) 1 [1..n]

term :: (Floating a, Integral b) => a -> b -> a
term x y = (x ^^ y) / fromIntegral(factorial y)

series :: (Floating a) => a -> [a]
series x = zipWith (*) ([term x exp | exp <- [1,3..]]) (cycle [1, -1])

sin' :: (Floating a) => a -> a
sin' x = foldl (+) 0 (take 30 (series x))

maclaurin :: (Floating a, Ord a) => [a] -> a -> a
maclaurin [] _ = 0
maclaurin [n] _ = n
maclaurin (x:xs) threshold
    | diff > threshold = x + (maclaurin xs threshold)
    | otherwise        = x
    where diff = abs (x - head xs)

sin'' :: (Floating a, Ord a) => a -> a -> a
sin'' x tolerance = maclaurin (series x) tolerance

test :: (Num a) => a -> a
test x = (2 * x ^ 2) + (5 * x) + 12

main = do
  print(simpsons test 1 3)
  print(trapezoidal test 1 3)
  print(sin' (3 * pi / 2))
  print(sin'' (pi / 2) 0.0000000000000000001)
