import unittest
from asaan.interpreter import Interpreter

class InterpreterTests(unittest.TestCase):
    def test_variables_and_print(self):
        output = []
        Interpreter(output_fn=output.append).execute('var.x/int = 7\nprint: x')
        self.assertEqual(output, [7])

    def test_calculation(self):
        output = []
        Interpreter(output_fn=output.append).execute('calc.calculate | 6 * (2 + 3)\nprint: calculate')
        self.assertEqual(output, [30])

    def test_loop(self):
        output = []
        Interpreter(output_fn=output.append).execute('for var.i/int in 1..3:\n    print: i')
        self.assertEqual(output, [1, 2, 3])

if __name__ == "__main__":
    unittest.main()
