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


def get_payer_list_from_string(payer_string):
    """returns RegisteredUser payer(s) from general string
    """
    return [payer_string]
