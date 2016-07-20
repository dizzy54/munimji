from django.test import TestCase

from users.models import *


class UsersTestCase(TestCase):
    def setUp(self):
        alice = RegisteredUser.objects.create(
            first_name='Alice',
            last_name='A.',
            fbid='alicea.'
        )
        bob = RegisteredUser.objects.create(
            first_name='Bob',
            last_name='B.',
            fbid='bobb.'
        )
        RegisteredUser.objects.create(
            first_name='Charlie',
            last_name='C.',
            fbid='charliec.'
        )
        RegisteredUser.objects.create(
            first_name='David',
            last_name='D.',
            fbid='davidd.'
        )

        Relationship.objects.create(
            from_user=alice,
            to_user=bob,
            balance=100.0,
        )

    def test_symmetry_in_friends(self):
        """tests if symmetrical relationship between friends is auto established
        """
        users = RegisteredUser.objects.all()
        count = users.count()

        bob = RegisteredUser.objects.get(fbid='bobb.')
        friend = bob.friends.first()
        relation = Relationship.objects.get(from_user=bob)
        balance = relation.balance

        self.assertEqual(count, 4)
        self.assertEqual(friend.fbid, 'alicea.')
        self.assertEqual(balance, -100.0)

    def test_transaction_with_single_contributor(self):
        """tests if valid transaction and corresponding relations are created with single contributor
        """
        a_contrib = 750.0
        b_contrib = 0.0
        c_contrib = 0.0
        consumption = (a_contrib + b_contrib + c_contrib) / 3
        data = [
            {
                'user_id': RegisteredUser.objects.get(first_name='Alice').pk,
                'contribution': a_contrib,
                'consumption': consumption
            },
            {
                'user_id': RegisteredUser.objects.get(first_name='Bob').pk,
                'contribution': b_contrib,
                'consumption': consumption
            },
            {
                'user_id': RegisteredUser.objects.get(first_name='Charlie').pk,
                'contribution': c_contrib,
                'consumption': consumption
            },
        ]
        Transaction.objects.create(input_data=data)
        a_b = Relationship.objects.get(
            from_user__first_name='Alice',
            to_user__first_name='Bob',
        ).balance
        a_c = Relationship.objects.get(
            from_user__first_name='Alice',
            to_user__first_name='Charlie',
        ).balance
        c_a = Relationship.objects.get(
            to_user__first_name='Alice',
            from_user__first_name='Charlie',
        ).balance
        b_c = Relationship.objects.get(
            from_user__first_name='Bob',
            to_user__first_name='Charlie',
        ).balance

        self.assertEqual(a_b, consumption + 100)
        self.assertEqual(a_c, consumption)
        self.assertEqual(c_a, -consumption)
        self.assertEqual(b_c, 0)

    def test_transaction_with_multiple_contributors(self):
        """tests if valid transaction and corresponding relations are created with multiple contributor
        """
        a_contrib = 750.0
        b_contrib = 300.0
        c_contrib = 0.0

        consumption = (a_contrib + b_contrib + c_contrib) / 3

        a_bal_b = (
            (a_contrib - consumption) * b_contrib / (3 * consumption) -
            (b_contrib - consumption) * a_contrib / (3 * consumption)
        )

        b_bal_c = (
            (b_contrib - consumption) * c_contrib / (3 * consumption) -
            (c_contrib - consumption) * b_contrib / (3 * consumption)
        )

        c_bal_a = (
            (c_contrib - consumption) * a_contrib / (3 * consumption) -
            (a_contrib - consumption) * c_contrib / (3 * consumption)
        )

        a_bal = a_contrib - consumption
        b_bal = b_contrib - consumption
        c_bal = c_contrib - consumption

        data = [
            {
                'user_id': RegisteredUser.objects.get(first_name='Alice').pk,
                'contribution': a_contrib,
                'consumption': consumption
            },
            {
                'user_id': RegisteredUser.objects.get(first_name='Bob').pk,
                'contribution': b_contrib,
                'consumption': consumption
            },
            {
                'user_id': RegisteredUser.objects.get(first_name='Charlie').pk,
                'contribution': c_contrib,
                'consumption': consumption
            },
        ]
        Transaction.objects.create(input_data=data)
        a_b = Relationship.objects.get(
            from_user__first_name='Alice',
            to_user__first_name='Bob',
        ).balance
        a_c = Relationship.objects.get(
            from_user__first_name='Alice',
            to_user__first_name='Charlie',
        ).balance
        c_a = Relationship.objects.get(
            to_user__first_name='Alice',
            from_user__first_name='Charlie',
        ).balance
        b_c = Relationship.objects.get(
            from_user__first_name='Bob',
            to_user__first_name='Charlie',
        ).balance

        print a_bal_b
        print b_bal_c
        print c_bal_a

        self.assertEqual(a_b, a_bal_b + 100)
        self.assertEqual(a_c, -c_bal_a)
        self.assertEqual(c_a, c_bal_a)
        self.assertEqual(b_c, b_bal_c)
        self.assertEqual(a_bal_b + -c_bal_a, a_bal)
        self.assertEqual(b_bal_c + -a_bal_b, b_bal)
        self.assertEqual(c_bal_a + -b_bal_c, c_bal)

    def test_transaction_with_multiple_contributors_unequal(self):
        """tests if valid transaction and corresponding relations are created with multiple contributors
        consumption unequal
        """
        a_contrib = 750.0
        b_contrib = 300.0
        c_contrib = 0.0

        consumption = (a_contrib + b_contrib + c_contrib) / 3

        a_consumption = 0.5 * consumption
        b_consumption = consumption
        c_consumption = 1.5 * consumption

        a_bal_b = (
            (a_contrib - a_consumption) * b_contrib / (3 * consumption) -
            (b_contrib - b_consumption) * a_contrib / (3 * consumption)
        )

        b_bal_c = (
            (b_contrib - b_consumption) * c_contrib / (3 * consumption) -
            (c_contrib - c_consumption) * b_contrib / (3 * consumption)
        )

        c_bal_a = (
            (c_contrib - c_consumption) * a_contrib / (3 * consumption) -
            (a_contrib - a_consumption) * c_contrib / (3 * consumption)
        )

        a_bal = a_contrib - a_consumption
        b_bal = b_contrib - b_consumption
        c_bal = c_contrib - c_consumption

        data = [
            {
                'user_id': RegisteredUser.objects.get(first_name='Alice').pk,
                'contribution': a_contrib,
                'consumption': a_consumption
            },
            {
                'user_id': RegisteredUser.objects.get(first_name='Bob').pk,
                'contribution': b_contrib,
                'consumption': b_consumption
            },
            {
                'user_id': RegisteredUser.objects.get(first_name='Charlie').pk,
                'contribution': c_contrib,
                'consumption': c_consumption
            },
        ]
        Transaction.objects.create(input_data=data)
        a_b = Relationship.objects.get(
            from_user__first_name='Alice',
            to_user__first_name='Bob',
        ).balance
        a_c = Relationship.objects.get(
            from_user__first_name='Alice',
            to_user__first_name='Charlie',
        ).balance
        c_a = Relationship.objects.get(
            to_user__first_name='Alice',
            from_user__first_name='Charlie',
        ).balance
        b_c = Relationship.objects.get(
            from_user__first_name='Bob',
            to_user__first_name='Charlie',
        ).balance

        print a_bal_b
        print b_bal_c
        print c_bal_a

        self.assertEqual(a_b, a_bal_b + 100)
        self.assertEqual(a_c, -c_bal_a)
        self.assertEqual(c_a, c_bal_a)
        self.assertEqual(b_c, b_bal_c)
        self.assertEqual(a_bal_b + -c_bal_a, a_bal)
        self.assertEqual(b_bal_c + -a_bal_b, b_bal)
        self.assertEqual(c_bal_a + -b_bal_c, c_bal)
