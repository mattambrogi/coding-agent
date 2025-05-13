def fizzbuzz(n):
    """
    Print numbers from 1 to n, but print 'Fizz' for multiples of 3,
    'Buzz' for multiples of 5, and 'FizzBuzz' for multiples of both.
    """
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)

if __name__ == "__main__":
    fizzbuzz(10)  # Run FizzBuzz from 1 to 10 when script is executed directly