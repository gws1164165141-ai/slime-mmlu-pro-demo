import unittest

from mmlu_reward import compute_reward, extract_answer


class TestMMLUReward(unittest.TestCase):
    def test_extract_final_answer(self):
        self.assertEqual(extract_answer("Reasoning...\nFinal answer: A"), "A")

    def test_extract_the_answer_is_parenthesized(self):
        self.assertEqual(extract_answer("The answer is (B)."), "B")

    def test_extract_answer_prefix(self):
        self.assertEqual(extract_answer("Answer: C"), "C")

    def test_extract_trailing_single_letter(self):
        self.assertEqual(extract_answer("After checking every option, I choose\nD"), "D")

    def test_extract_no_answer(self):
        self.assertIsNone(extract_answer("I cannot determine the correct option."))

    def test_correct_reward(self):
        self.assertEqual(compute_reward("Final answer: E", "E"), 1.0)

    def test_wrong_reward(self):
        self.assertEqual(compute_reward("Final answer: F", "E"), 0.0)

    def test_invalid_label(self):
        self.assertEqual(compute_reward("Final answer: A", "K"), 0.0)


if __name__ == "__main__":
    unittest.main()
