from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models

from witio import splitwise

import re


class RegisteredUser(models.Model):

    class Meta:
        verbose_name = 'Registered user'
        verbose_name_plural = 'Registered users'

    def __str__(self):
        return str(self.first_name + ' ' + self.last_name)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    fbid = models.CharField(max_length=20)

    splitwise_id = models.CharField(max_length=20, null=True)
    splitwise_first_name = models.CharField(max_length=30, null=True)
    splitwise_last_name = models.CharField(max_length=30, null=True)
    splitwise_email = models.CharField(max_length=60, null=True)

    friends = models.ManyToManyField(
        'self',
        symmetrical=False,
        through='Relationship',
        through_fields=('from_user', 'to_user'),
    )

    resource_owner_key = models.CharField(max_length=60, null=True)
    resource_owner_secret = models.CharField(max_length=60, null=True)
    oauth_verifier = models.CharField(max_length=30, null=True)

    # permanent access keys
    splitwise_key = models.CharField(max_length=60, null=True)
    splitwise_secret = models.CharField(max_length=60, null=True)

    def add_friend(self, friend_id):
        """add existing user as friend
        returns True if new friend added
        """
        if Relationship.objects.filter(from_user_id=self.pk, to_user_id=friend_id).exists():
            return False
        else:
            friend = RegisteredUser.objects.filter(id=friend_id)
            if friend.count() == 1:
                friend = friend[0]
                Relationship.objects.create(from_user=self, to_user=friend, balance=0.0)
                return True
            else:
                return False

    def get_splitwise_id_list_from_names_string(self, names_string):
        """returns list of splitwise ids from names string. Also returns unidentified names
        """
        first_level_entities = re.split(',|;|and|&', names_string)
        
    def get_splitwise_auth_link(self):
        oauth, resource_owner_key, resource_owner_secret = splitwise.get_request_token()
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.save()
        base_authorization_url = 'https://secure.splitwise.com/authorize'
        return oauth.authorization_url(base_authorization_url)

    def get_splitwise_credentials(self):
        if self.splitwise_key and self.splitwise_secret:
            if not self.splitwise_id:
                user_details = splitwise.get_user_by_auth(self.splitwise_key, self.splitwise_secret)
                self.splitwise_id = user_details.get('id')
                self.splitwise_first_name = user_details.get('first_name')
                self.splitwise_last_name = user_details.get('last_name')
                self.splitwise_email = user_details.get('email')
                self.save()
            return self.splitwise_key, self.splitwise_secret
        else:
            return None


class Relationship(models.Model):
    from_user = models.ForeignKey(RegisteredUser, related_name='from_relationship')
    to_user = models.ForeignKey(RegisteredUser, related_name='to_relationship')
    balance = models.FloatField()

    def update_symmetric_relation(self):
        if self.from_user in self.to_user.friends.all():
            # print 'if'
            relation = Relationship.objects.get(from_user_id=self.to_user.pk, to_user_id=self.from_user.pk)
            if abs(relation.balance + self.balance) >= 0.0001:
                relation.balance = -self.balance
                relation.save()
        else:
            # print 'else'
            Relationship.objects.create(from_user=self.to_user, to_user=self.from_user, balance=-self.balance)

    def save(self, *args, **kwargs):
        # print 'from ' + self.from_user.first_name
        # print 'to ' + self.to_user.first_name
        # print 'balance = ' + str(self.balance)
        super(Relationship, self).save(*args, **kwargs)
        self.update_symmetric_relation()


class Transaction(models.Model):
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return str(self.modified)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    users = models.ManyToManyField(
        RegisteredUser,
        through='TransactionBit',
        through_fields=('transaction', 'from_user'),
    )

    input_data = JSONField()

    def _update_bits(self, data):
        """
        creates transaction and adds to db from list of form
        [
            {'user_id': 1, 'contribution': 500, 'consumption': 125},
            ...
            {}
        ]
        returns created = True / False
        """
        # delete existing bits, if any
        self.users.clear()

        # create bit dictionary
        total_contribution = 0
        total_consumption = 0
        contributor_list = []
        user_id_list = [item['user_id'] for item in data]
        # validate users
        for entry in data:
            if not RegisteredUser.objects.filter(id=entry['user_id']).exists():
                return False
        # setup
        for entry in data:
            total_contribution += entry['contribution']
            total_consumption += entry['consumption']
            if entry['contribution'] > 0:
                contributor_list.append({
                    'user_id': entry['user_id'],
                    'contribution': entry['contribution']
                })
            # add as friend with rest of users
            if len(user_id_list) > 1:
                user_id_list = user_id_list[1:]
                user = RegisteredUser.objects.get(id=entry['user_id'])
                for friend_id in user_id_list:
                    user.add_friend(friend_id)

        if total_consumption != total_contribution:
            return False

        # add new bits
        for entry in data:
            consumer = RegisteredUser.objects.get(pk=entry['user_id'])
            net_consumption = entry['consumption'] - entry['contribution']
            for contrib_entry in contributor_list:
                contributor = RegisteredUser.objects.get(pk=contrib_entry['user_id'])
                if consumer.pk == contributor.pk:
                    pass
                else:
                    amount_owed_by_consumer = net_consumption * contrib_entry['contribution'] / total_contribution
                    TransactionBit.objects.create(
                        from_user=contributor,
                        to_user=consumer,
                        transaction=self,
                        amount_owed_by_to_user=amount_owed_by_consumer,
                    )

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)  # for transaction to link to bits
        self._update_bits(self.input_data)
        # super(Transaction, self).save(*args, **kwargs)  # to save updated bits


class TransactionBit(models.Model):
    class Meta:
        verbose_name = 'Transaction bit'
        verbose_name_plural = 'Transaction bits'

    from_user = models.ForeignKey(RegisteredUser, related_name='from_transaction_bit')
    transaction = models.ForeignKey(Transaction)
    to_user = models.ForeignKey(RegisteredUser, related_name='to_transaction_bit')
    amount_owed_by_to_user = models.FloatField()

    def _update_relationship(self, amount):
        """
        update relationship between users
        """
        # if relationship exists (assumes symmetry)
        if self.to_user in self.from_user.friends.all():
            relation = Relationship.objects.get(
                from_user_id=self.from_user.pk,
                to_user_id=self.to_user.pk
            )
            relation.balance += amount
            relation.save()
        # if it doesn't, create new
        else:
            Relationship.objects.create(from_user=self.from_user, to_user=self.to_user, balance=amount)

    def save(self, *args, **kwargs):
        """overriden to update relationship between from_user and to_user
        """
        self._update_relationship(amount=self.amount_owed_by_to_user)
        super(TransactionBit, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """overriden to update relationship between from_user and to_user
        """
        self._update_relationship(amount=-self.amount_owed_by_to_user)
        super(TransactionBit, self).delete(*args, **kwargs)
