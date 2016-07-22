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

    def process_text_query(self, text):
        """processes any text query recieved from client
        - runs any required actions
        - sends response
        """
        request = self.text_request()
        request.query = text
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
        return {'split': self._split}

    def _split(self, response):
        pass
