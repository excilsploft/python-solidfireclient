import unittest


class TestUnitTest(unittest.TestCase):
    def test_nothing(self):
        self.assertEqual(1, 1)

    def test_fail_nothing(self):
        self.assertNotEqual(0, 1)
