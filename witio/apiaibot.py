import json
import time

from django.conf import settings
import apiai

import fb
import splitwise
import stringops
from witio.models import Session
# from users.models import RegisteredUser

CLIENT_ACCESS_TOKEN = settings.APIAI_ACCESS_TOKEN

APIAI_CODE_TAG = '#code!-'

class MyApiaiClient(apiai.ApiAI):
    """custom apiai client
    """
    def __init__(self, session_id=None):
        super(MyApiaiClient, self).__init__(
            client_access_token=CLIENT_ACCESS_TOKEN,
            session_id=session_id,
        )

    def process_text_query(self, text, added_contexts=None, reset_contexts=False):
        """processes any text query recieved from client
        - runs any required actions
        - sends response
        """
        request = self.text_request()
        request.query = text
        request.resetContexts = reset_contexts

        # context handling
        contexts = request.contexts

        '''
        if deleted_context_names:
            for context in contexts:
                if context['name'] in deleted_context_names:
                    contexts.remove(context)
        '''

        if added_contexts:
            for added_context in added_contexts:
                contexts.append(added_context)

        request.contexts = contexts

        print "context = %s " % contexts
        response = json.loads(request.getresponse().read())

        print 'response' + str(response)

        try:
            result = response['result']
        except KeyError:
            # error response
            print response
            return
        action = result.get('action')
        actionIncomplete = result.get('actionIncomplete', False)
        message = response['result']['fulfillment']['speech']
        print "message - " + str(message) + "type=" + str(type(message))

        session = Session.objects.get(session_id=self.session_id)
        fbid = session.fbid

        if action:
            # check if authenticated with splitwise
            user = session.user
            splitwise_creds = user.get_splitwise_credentials()
            if splitwise_creds:
                # to test
                access_token, access_token_secret = splitwise_creds
                # check if action is completed
                if not actionIncomplete:
                    action_func = self.actions().get(action)
                    if action_func:
                        action_message = action_func(response, fbid, user)
                        fb.send_long_message(fbid, action_message)
                        # wait to cause delay between this and the next message
                        # time.sleep(2)
            else:
                auth_link = user.get_splitwise_auth_link()
                message = '''to continue, please log into your splitwise account by clicking here
                 - %s''' % auth_link

        fb.send_message(fbid, message)

    def actions(self):
        """returns a dictionary of actions
        """
        return {
            'split': self._split,
            'verify_payer': self._verify_payer,
            'show_summary': self._show_summary,
        }

    def _split(self, response, fbid, user):
        print "split action triggered"
        # payer_missing = False
        # payee_missing = False
        # amount_missing = False
        # get friend list
        '''
        friends = splitwise.get_friends(splitwise_creds[0], splitwise_creds[1])
        friend_list = friends.get('friends')
        friend_name_list = []
        for friend in friend_list:
            first_name = friend.get('first_name', '')
            if first_name is None:
                first_name = ''
            # print 'first name = ' + str(first_name)
            last_name = friend.get('last_name', '')
            if last_name is None:
                last_name = ''
            # print 'last name = ' + str(last_name)
            full_name = first_name + ' ' + last_name
            friend_name_list.append(full_name)
        '''

        payer_string = response['result']['parameters']['payer']
        payee_string = response['result']['parameters']['payees']
        amount_paid_string = response['result']['parameters']['amount_paid']

        # check if response is tagged by code
        tag = response['result']['parameters'].get('tag')
        payer_is_tagged = True if tag and tag == APIAI_CODE_TAG + 'payer' else False
        payees_is_tagged = True if tag and tag == APIAI_CODE_TAG + 'payer,payees' else False

        friend_name_list = None
        # get payers
        if payer_is_tagged:
            # payer_string = payer_string
            pass
        else:
            # payer_names = stringops.match_from_name_list(payer_string, friend_name_list)
            payer_names, friend_name_list = user.get_splitwise_matches_from_name_string(payer_string)
            print "payer names = " + str(payer_names)
            response_string = stringops.get_response_string_from_matched_names(payer_names, payee=False)
            print "response string = " + str(response_string)
            if not response_string:
                # names matched perfectly
                if payer_names[0]:
                    # names exist in match_list other than self
                    # payer_list = [friend_list[payer[1]] for payer in payer_names]
                    payer_string = ', '.join([friend_name_list[payer[1]] for payer in payer_names])
                    if payer_names[3]:
                        payer_string = 'you, ' + payer_string
                else:
                    payer_string = 'you'
            else:
                fb.send_message(fbid, response_string)
                payer_string = None
                added_contexts = None
                message = 'payees: %s, amount: %s' % (payee_string, amount_paid_string)
                print 'message = ' + message
                self.process_text_query(message, added_contexts=added_contexts, reset_contexts=True)
                return None

        # get payees
        if payees_is_tagged:
            # payee_string = payee_string
            pass
        else:
            # payee_names = stringops.match_from_name_list(payee_string, friend_name_list)
            payee_names = user.get_splitwise_matches_from_name_string(
                payee_string,
                friend_name_list=friend_name_list
            )[0]
            print "payee names = " + str(payee_names)
            response_string = stringops.get_response_string_from_matched_names(payee_names, payee=True)
            print "response string = " + str(response_string)
            if not response_string:
                # names matched perfectly
                if payee_names[0]:
                    # names exist in match_list other than self
                    # payee_list = [friend_list[payee[1]] for payee in payee_names]
                    payee_string = ', '.join([friend_name_list[payee[1]] for payee in payee_names])
                    if payee_names[3]:
                        payee_string = 'you, ' + payee_string
                else:
                    payee_string = 'you'
            else:
                fb.send_message(fbid, response_string)
                payee_string = None
                added_contexts = None
                message = APIAI_CODE_TAG + 'payer payers: %s, amount: %s' % (payer_string, amount_paid_string)
                print 'message = ' + message
                self.process_text_query(message, added_contexts=added_contexts, reset_contexts=True)
                return None

        # get amount

        message = 'Adding transaction of amount %s - paid by %s, between %s, split equally' % (
            amount_paid_string, payer_string, payee_string
        )
        return message

    def _show_summary(self, response, fbid, user):
        friend_list = user.get_splitwise_friend_list()
        summary_list = []
        for friend in friend_list:
            '''
            friend_dict = {
                'first_name': friend['first_name'],
                'last_name': friend['last_name'],
                'balance': friend['balance']
            }
            '''
            balance = friend['balance'][0]
            amount = str(balance['amount'])
            currency = balance['currency_code']

            first_name = friend.get('first_name', '')
            if first_name == 'None':
                first_name = ''
            last_name = friend.get('last_name', '')
            if last_name == '':
                last_name = ''

            if amount[0] != '-':
                friend_str = '%s %s - Owes you %s %s' % (first_name, last_name, currency, amount)
            else:
                friend_str = '%s %s - You owe %s %s' % (first_name, last_name, currency, amount[1:])
            summary_list.append(friend_str)
        message = '\n'.join(summary_list)
        return message

    def _verify_payer(self, response, fbid, user):
        print "verify_payer action triggered"
        payer_string = response['result']['parameters']['payer']
        '''
        payer_list = get_payer_list_from_string(payer_string)

        if payer_list:
            payer_display_names = payer_list[0]
        '''
        # deleted_contexts = []
        added_contexts = None
        message = APIAI_CODE_TAG + 'split_start payers: ' + payer_string
        self.process_text_query(message, added_contexts=added_contexts)
        return None


def get_payer_list_from_string(payer_string):
    """returns RegisteredUser payer(s) from general string
    """
    return [payer_string]
