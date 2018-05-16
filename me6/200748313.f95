program maclaurin
    implicit none
    double precision :: x
    integer :: term
    print "(a)", "Input x term:"
    read *, x, term
    x = sine(x, term)
    print *, x

contains
    function factorial (n)
        implicit none
        double precision :: factorial
        integer :: n, i

        factorial = 1
        if (n > 0) then
            do i = 2, n
                factorial = factorial * i
            end do
        end if
    end function factorial

    function sine(x, term)
        implicit none
        double precision :: x, sine
        integer :: term, exp, i, sign
        sine = 0
        if (term > 0) then
            do i = 0, term - 1
                exp = (2 * i) + 1
                sign = (-1) ** i
                sine = sine + sign * (x ** exp / factorial(exp))
            end do
        end if
    end function sine
end program maclaurin
