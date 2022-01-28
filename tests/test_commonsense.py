from unittest import TestCase
from wafl.qa.common_sense import CommonSense


class TestCommonSense(TestCase):
    def test_common_sense_positive(self):
        claim = "'pasta' belongs to a grocery list"
        common_sense = CommonSense()
        answer = common_sense.claim_makes_sense(claim)
        print(answer)
        assert answer.text == "True"
