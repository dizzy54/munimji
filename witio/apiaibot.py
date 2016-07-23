import json

from django.conf import settings
import apiai

import fb
from witio.models import Session

CLIENT_ACCESS_TOKEN = settings.APIAI_ACCESS_TOKEN


class MyApiaiClient(apiai.ApiAI):
    """custom apiai client
    """
    def __init__(self, session_id=None):
        super(MyApiaiClient, self).__init__(
            client_access_token=CLIENT_ACCESS_TOKEN,
            session_id=session_id,
        )

    def process_text_query(self, text, added_context=None):
        """processes any text query recieved from client
        - runs any required actions
        - sends response
        """
        request = self.text_request()
        request.query = text
        if added_context:
            contexts = request.contexts
            contexts.append(added_context)
            request.contexts = contexts

        response = json.loads(request.getresponse().read())
        result = response['result']
        action = result.get('action')
        actionIncomplete = result.get('actionIncomplete', False)
        message = response['result']['fulfillment']['speech']

        if action is not None:
            if not actionIncomplete:
                action_func = self.actions().get(action)
                if action_func:
                    action_func(response)

        session = Session.objects.get(session_id=self.session_id)
        fbid = session.fbid
        fb.send_message(fbid, message)

    def actions(self):
        """returns a dictionary of actions
        """
        return {
            'split': self._split,
            'verify_payer': self._verify_payer,
        }

    def _split(self, response):
        print "split action triggered"
        pass

    def _verify_payer(self, response):
        print "verify_payer action triggered"
        payer_string = response['parameters']['payer']
        payer_list = get_payer_list_from_string(payer_string)
        if payer_list:
            payer_display_names = payer_list[0]
            added_context = {
                'name': 'payer_processed_code',
                'lifespan': 5,
                'parameters': {
                    'verified_payer_string': payer_display_names
                }
            }
            self.process_text_query("payer verified", added_context=added_context)


def get_payer_list_from_string(payer_string):
    """returns RegisteredUser payer(s) from general string
    """
    return [payer_string]
