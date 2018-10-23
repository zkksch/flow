import unittest
from enum import Enum

from flow.bases import FlowBase, RuleBase
from flow.exceptions import TransferError
from flow.rules import AllToAllRule
from flow.rules import AllToOneRule
from flow.rules import AllToManyRule
from flow.rules import OneToAllRule
from flow.rules import ManyToAllRule
from flow.rules import OneToOneRule
from flow.rules import OneToManyRule
from flow.rules import ManyToOneRule
from flow.rules import ManyToManyRule
from flow.rules import RuleList


class TestFlow(unittest.TestCase):
    def setUp(self):
        class Week(Enum):
            MONDAY = 0
            TUESDAY = 1
            WEDNESDAY = 2
            THURSDAY = 3
            FRIDAY = 4
            SATURDAY = 5
            SUNDAY = 6

        self.week = Week

    def test_flow_transfer(self):
        r = RuleList((
            OneToAllRule(None),
            AllToOneRule(None),
            OneToOneRule(self.week.MONDAY, self.week.TUESDAY),
            OneToOneRule(self.week.TUESDAY, self.week.WEDNESDAY),
            OneToOneRule(self.week.WEDNESDAY, self.week.THURSDAY),
            OneToOneRule(self.week.THURSDAY, self.week.FRIDAY),
            OneToOneRule(self.week.FRIDAY, self.week.SATURDAY),
            OneToOneRule(self.week.SATURDAY, self.week.SUNDAY),
            OneToOneRule(self.week.SUNDAY, self.week.MONDAY),
        ))

        f = FlowBase(r)

        transfers_order = [
            self.week.MONDAY,
            self.week.TUESDAY,
            self.week.WEDNESDAY,
            self.week.THURSDAY,
            self.week.FRIDAY,
            self.week.SATURDAY,
            self.week.SUNDAY,
            None
        ]

        prev = None

        for next_value in transfers_order:
            current = f.value
            self.assertEqual(current, prev)
            f.value = next_value
            self.assertEqual(f.value, next_value)
            prev = f.value

        error_cases = [
            (self.week.MONDAY, self.week.WEDNESDAY),
            (self.week.WEDNESDAY, self.week.FRIDAY),
            (self.week.SUNDAY, self.week.TUESDAY),
            (self.week.MONDAY, object()),
            (object(), self.week.MONDAY),
            (object(), object()),
        ]

        for init_value, transfer_value in error_cases:
            f = FlowBase(r, init=init_value)
            with self.assertRaises(TransferError):
                f.value = transfer_value

    def _check_rule_cases(self, rule, cases):
        for input_value, output_value, result in cases:
            is_valid, error = rule.is_valid(input_value, output_value)
            self.assertEqual(is_valid, result)

            rules_list = RuleList((rule,))
            is_valid, error = rules_list.is_valid(input_value, output_value)
            self.assertEqual(is_valid, result)

    def test_one_to_one_rule(self):
        cases = [
            (self.week.MONDAY, self.week.TUESDAY, True),

            (self.week.TUESDAY, self.week.MONDAY, False),
            (self.week.MONDAY, self.week.WEDNESDAY, False),

            (self.week.MONDAY, object(), False),
            (object(), self.week.MONDAY, False),
            (object(), object(), False),
        ]

        rule = OneToOneRule(self.week.MONDAY, self.week.TUESDAY)
        self._check_rule_cases(rule, cases)

    def test_one_to_many_rule(self):
        cases = [
            (self.week.MONDAY, self.week.TUESDAY, True),
            (self.week.MONDAY, self.week.WEDNESDAY, True),
            (self.week.MONDAY, self.week.THURSDAY, True),

            (self.week.MONDAY, self.week.FRIDAY, False),
            (self.week.TUESDAY, self.week.WEDNESDAY, False),

            (self.week.MONDAY, object(), False),
            (object(), self.week.TUESDAY, False),
            (object(), object(), False),
        ]

        rule = OneToManyRule(self.week.MONDAY, (
            self.week.TUESDAY,
            self.week.WEDNESDAY,
            self.week.THURSDAY,
        ))

        self._check_rule_cases(rule, cases)

    def test_many_to_one_rule(self):
        cases = [
            (self.week.TUESDAY, self.week.MONDAY, True),
            (self.week.WEDNESDAY, self.week.MONDAY, True),
            (self.week.THURSDAY, self.week.MONDAY, True),

            (self.week.FRIDAY, self.week.MONDAY, False),
            (self.week.WEDNESDAY, self.week.TUESDAY, False),

            (self.week.TUESDAY, object(), False),
            (object(), self.week.MONDAY, False),
            (object(), object(), False),
        ]

        rule = ManyToOneRule((
            self.week.TUESDAY,
            self.week.WEDNESDAY,
            self.week.THURSDAY,
        ), self.week.MONDAY)

        self._check_rule_cases(rule, cases)

    def test_many_to_many_rule(self):
        cases = [
            (self.week.MONDAY, self.week.THURSDAY, True),
            (self.week.MONDAY, self.week.FRIDAY, True),
            (self.week.MONDAY, self.week.SATURDAY, True),

            (self.week.TUESDAY, self.week.THURSDAY, True),
            (self.week.TUESDAY, self.week.FRIDAY, True),
            (self.week.TUESDAY, self.week.SATURDAY, True),

            (self.week.WEDNESDAY, self.week.THURSDAY, True),
            (self.week.WEDNESDAY, self.week.FRIDAY, True),
            (self.week.WEDNESDAY, self.week.SATURDAY, True),

            (self.week.MONDAY, self.week.SUNDAY, False),
            (self.week.TUESDAY, self.week.SUNDAY, False),
            (self.week.WEDNESDAY, self.week.SUNDAY, False),

            (self.week.TUESDAY, self.week.MONDAY, False),
            (self.week.WEDNESDAY, self.week.MONDAY, False),

            (self.week.THURSDAY, self.week.SUNDAY, False),
            (self.week.FRIDAY, self.week.SUNDAY, False),
            (self.week.SATURDAY, self.week.SUNDAY, False),

            (self.week.FRIDAY, self.week.THURSDAY, False),
            (self.week.SATURDAY, self.week.THURSDAY, False),

            (self.week.MONDAY, object(), False),
            (self.week.TUESDAY, object(), False),
            (self.week.WEDNESDAY, object(), False),
            (object(), self.week.THURSDAY, False),
            (object(), self.week.FRIDAY, False),
            (object(), self.week.SATURDAY, False),
            (object(), object(), False),
        ]

        rule = ManyToManyRule(
            (
                self.week.MONDAY,
                self.week.TUESDAY,
                self.week.WEDNESDAY,
            ),
            (
                self.week.THURSDAY,
                self.week.FRIDAY,
                self.week.SATURDAY,
            )
        )

        self._check_rule_cases(rule, cases)

    def test_one_to_all_rule(self):
        cases = [
            (self.week.MONDAY, self.week.MONDAY, True),
            (self.week.MONDAY, self.week.TUESDAY, True),
            (self.week.MONDAY, self.week.WEDNESDAY, True),
            (self.week.MONDAY, self.week.THURSDAY, True),
            (self.week.MONDAY, self.week.FRIDAY, True),
            (self.week.MONDAY, self.week.SATURDAY, True),
            (self.week.MONDAY, self.week.SUNDAY, True),

            (self.week.TUESDAY, self.week.MONDAY, False),
            (self.week.TUESDAY, self.week.WEDNESDAY, False),

            (self.week.MONDAY, object(), True),
            (object(), self.week.MONDAY, False),
            (object(), object(), False),
        ]

        rule = OneToAllRule(self.week.MONDAY)

        self._check_rule_cases(rule, cases)

    def test_all_to_one_rule(self):
        cases = [
            (self.week.MONDAY, self.week.MONDAY, True),
            (self.week.TUESDAY, self.week.MONDAY, True),
            (self.week.WEDNESDAY, self.week.MONDAY, True),
            (self.week.THURSDAY, self.week.MONDAY, True),
            (self.week.FRIDAY, self.week.MONDAY, True),
            (self.week.SATURDAY, self.week.MONDAY, True),
            (self.week.SUNDAY, self.week.MONDAY, True),

            (self.week.MONDAY, self.week.TUESDAY, False),
            (self.week.TUESDAY, self.week.WEDNESDAY, False),

            (self.week.MONDAY, object(), False),
            (object(), self.week.MONDAY, True),
            (object(), object(), False),
        ]

        rule = AllToOneRule(self.week.MONDAY)

        self._check_rule_cases(rule, cases)

    def test_many_to_all_rule(self):
        cases = [
            (self.week.MONDAY, self.week.MONDAY, True),
            (self.week.MONDAY, self.week.TUESDAY, True),
            (self.week.MONDAY, self.week.WEDNESDAY, True),
            (self.week.MONDAY, self.week.THURSDAY, True),
            (self.week.MONDAY, self.week.FRIDAY, True),
            (self.week.MONDAY, self.week.SATURDAY, True),
            (self.week.MONDAY, self.week.SUNDAY, True),

            (self.week.TUESDAY, self.week.MONDAY, True),
            (self.week.TUESDAY, self.week.TUESDAY, True),
            (self.week.TUESDAY, self.week.WEDNESDAY, True),
            (self.week.TUESDAY, self.week.THURSDAY, True),
            (self.week.TUESDAY, self.week.FRIDAY, True),
            (self.week.TUESDAY, self.week.SATURDAY, True),
            (self.week.TUESDAY, self.week.SUNDAY, True),

            (self.week.WEDNESDAY, self.week.MONDAY, True),
            (self.week.WEDNESDAY, self.week.TUESDAY, True),
            (self.week.WEDNESDAY, self.week.WEDNESDAY, True),
            (self.week.WEDNESDAY, self.week.THURSDAY, True),
            (self.week.WEDNESDAY, self.week.FRIDAY, True),
            (self.week.WEDNESDAY, self.week.SATURDAY, True),
            (self.week.WEDNESDAY, self.week.SUNDAY, True),

            (self.week.THURSDAY, self.week.MONDAY, False),
            (self.week.THURSDAY, self.week.TUESDAY, False),
            (self.week.THURSDAY, self.week.WEDNESDAY, False),

            (self.week.MONDAY, object(), True),
            (self.week.TUESDAY, object(), True),
            (self.week.WEDNESDAY, object(), True),
            (object(), self.week.MONDAY, False),
            (object(), object(), False),
        ]

        rule = ManyToAllRule((
            self.week.MONDAY,
            self.week.TUESDAY,
            self.week.WEDNESDAY,
        ))

        self._check_rule_cases(rule, cases)

    def test_all_to_many_rule(self):
        cases = [
            (self.week.MONDAY, self.week.MONDAY, True),
            (self.week.TUESDAY, self.week.MONDAY, True),
            (self.week.WEDNESDAY, self.week.MONDAY, True),
            (self.week.THURSDAY, self.week.MONDAY, True),
            (self.week.FRIDAY, self.week.MONDAY, True),
            (self.week.SATURDAY, self.week.MONDAY, True),
            (self.week.SUNDAY, self.week.MONDAY, True),

            (self.week.MONDAY, self.week.TUESDAY, True),
            (self.week.TUESDAY, self.week.TUESDAY, True),
            (self.week.WEDNESDAY, self.week.TUESDAY, True),
            (self.week.THURSDAY, self.week.TUESDAY, True),
            (self.week.FRIDAY, self.week.TUESDAY, True),
            (self.week.SATURDAY, self.week.TUESDAY, True),
            (self.week.SUNDAY, self.week.TUESDAY, True),

            (self.week.MONDAY, self.week.WEDNESDAY, True),
            (self.week.TUESDAY, self.week.WEDNESDAY, True),
            (self.week.WEDNESDAY, self.week.WEDNESDAY, True),
            (self.week.THURSDAY, self.week.WEDNESDAY, True),
            (self.week.FRIDAY, self.week.WEDNESDAY, True),
            (self.week.SATURDAY, self.week.WEDNESDAY, True),
            (self.week.SUNDAY, self.week.WEDNESDAY, True),

            (self.week.MONDAY, self.week.THURSDAY, False),
            (self.week.TUESDAY, self.week.THURSDAY, False),
            (self.week.WEDNESDAY, self.week.THURSDAY, False),

            (self.week.MONDAY, object(), False),
            (object(), self.week.MONDAY, True),
            (object(), self.week.TUESDAY, True),
            (object(), self.week.WEDNESDAY, True),
            (object(), object(), False),
        ]

        rule = AllToManyRule((
            self.week.MONDAY,
            self.week.TUESDAY,
            self.week.WEDNESDAY,
        ))

        self._check_rule_cases(rule, cases)

    def test_all_to_all_rule(self):
        cases = [
            (object(), object(), True),
            (None, object(), True),
            (object(), None, True),
        ]
        rule = AllToAllRule()

        self._check_rule_cases(rule, cases)

    def test_rules_list_rule_operator(self):
        week = self.week

        class CustomRule(RuleBase):
            @property
            def inputs(self):
                return {week.MONDAY}

            @property
            def outputs(self):
                return {week.TUESDAY, week.WEDNESDAY}

            def is_valid(self, input_value, output_value, context=None):
                if output_value == week.TUESDAY:
                    return False, ''
                else:
                    return True, None

        rule_all = RuleList((
            RuleList((
                OneToOneRule(self.week.MONDAY, self.week.TUESDAY),
                OneToOneRule(self.week.MONDAY, self.week.WEDNESDAY),
            )),
            CustomRule(),
        ), operator=all)

        rule_any = RuleList((
            RuleList((
                OneToOneRule(self.week.MONDAY, self.week.TUESDAY),
                OneToOneRule(self.week.MONDAY, self.week.WEDNESDAY),
            )),
            CustomRule(),
        ), operator=any)

        cases_all = [
            (self.week.MONDAY, self.week.TUESDAY, False),
            (self.week.MONDAY, self.week.WEDNESDAY, True),
            (self.week.TUESDAY, self.week.WEDNESDAY, False),
        ]

        cases_any = [
            (self.week.MONDAY, self.week.TUESDAY, True),
            (self.week.MONDAY, self.week.WEDNESDAY, True),
            (self.week.TUESDAY, self.week.WEDNESDAY, False),
        ]

        self._check_rule_cases(rule_all, cases_all)
        self._check_rule_cases(rule_any, cases_any)

    def test_transfer_context(self):
        week = self.week

        class CustomRule(RuleBase):
            @property
            def inputs(self):
                return {self.ALL}  # pragma: no cover

            @property
            def outputs(self):
                return {self.ALL}  # pragma: no cover

            def is_valid(self, input_value, output_value, context=None):
                if context is not None:
                    used = context.get('used', False)
                    if used:
                        return False, 'used'
                    else:
                        context['used'] = True
                        return True, None

                return True, None  # pragma: no cover

        flow = FlowBase(CustomRule(), week.MONDAY, {})

        flow.value = week.TUESDAY

        self.assertIn('used', flow.context)
        self.assertTrue(flow.context['used'])

        with self.assertRaises(TransferError):
            flow.value = week.MONDAY

        flow = FlowBase(CustomRule(), week.MONDAY, {'used': True})

        self.assertIn('used', flow.context)
        self.assertTrue(flow.context['used'])

        with self.assertRaises(TransferError):
            flow.value = week.MONDAY


if __name__ == '__main__':
    unittest.main()
