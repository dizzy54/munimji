import json

from django.conf import settings
import apiai

import fb
import splitwise
from witio.models import Session
# from users.models import RegisteredUser

CLIENT_ACCESS_TOKEN = settings.APIAI_ACCESS_TOKEN


class MyApiaiClient(apiai.ApiAI):
    """custom apiai client
    """
    def __init__(self, session_id=None):
        super(MyApiaiClient, self).__init__(
            client_access_token=CLIENT_ACCESS_TOKEN,
            session_id=session_id,
        )

    def process_text_query(self, text, added_contexts=None, deleted_context_names=None):
        """processes any text query recieved from client
        - runs any required actions
        - sends response
        """
        request = self.text_request()
        request.query = text

        # context handling
        contexts = request.contexts

        if deleted_context_names:
            for context in contexts:
                if context['name'] in deleted_context_names:
                    contexts.remove(context)

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
                        action_message = action_func(response, splitwise_creds)
                        fb.send_long_message(fbid, action_message)

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

    def _split(self, response, splitwise_creds):
        print "split action triggered"
        return None

    def _show_summary(self, response, splitwise_creds):
        friends = splitwise.get_friends(splitwise_creds[0], splitwise_creds[1])
        friend_list = friends.get('friends')
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
            amount = balance['amount']
            currency = balance['currency']
            if amount[0] == '-':
                friend_str = '%s %s - owes you %s%s' % (friend['first_name'], friend['last_name'], currency, amount)
            else:
                friend_str = '%s %s - You owe %s%s' % (friend['first_name'], friend['last_name'], currency, amount)
            summary_list.append(friend_str)
        message = '\n'.join(summary_list)
        return message

    def _verify_payer(self, response, splitwise_creds):
        print "verify_payer action triggered"
        payer_string = response['result']['parameters']['payer']
        payer_list = get_payer_list_from_string(payer_string)

        if payer_list:
            payer_display_names = payer_list[0]
            '''
            added_contexts = [{
                'name': 'payer_processed_code',
                'lifespan': 1,
                'parameters': {
                    'verified_payer_string': payer_display_names
                }
            }]
            # deleted_contexts = []
            '''
            added_contexts = None
            self.process_text_query(payer_display_names + " paid", added_contexts=added_contexts)
        return None


def get_payer_list_from_string(payer_string):
    """returns RegisteredUser payer(s) from general string
    """
    return [payer_string]
