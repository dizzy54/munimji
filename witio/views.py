import json
import requests
# import re
# from pprint import pprint
# import settings
from wit import Wit
from datetime import datetime

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = 'EAARlALJSWxoBANm5ybZAzd45BkXZCxZAr6bBZAiHXXdVVwYv4T6wmmII5X0aXUxqMgCQsC2Dshd8gCcYflZAAekFnsBGW2BVvC86w7aaRkzeNGgWn85V3iXb52GZChSsOZBBZCJYK790AaL5kAj2rvO4x5UW4iPmn2hBuZCeyZBB6KVgZDZD'
VERIFY_TOKEN = 'munimji_is_a_smartass'
WIT_ACCESS_TOKEN = 'JJ4K4KISLXHRRY2WQ4NU7PXRLEXUDMSL'


class WitioView(generic.View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            # basic inital setup here
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        print "Handling Messages"
        payload = request.body
        print payload
        data = json.loads(payload)
        messaging_entries = data["entry"][0]
        if "messaging" in messaging_entries and "message" in messaging_entries["messaging"][0]:
            # setup wit client
            def send(request, response):
                print(response['text'])

            def set_split(request):
                context = request['context']
                entities = request['entities']
                context['amount_split'] = 100
                return context

            actions = {
                'send': send,
                'setSplit': set_split,
            }

            wit_client = Wit(access_token=WIT_ACCESS_TOKEN, actions=actions)

            for sender, message in self.messaging_events(messaging_entries):
                print "Incoming from %s: %s" % (sender, message)
                session_id = sender + datetime.now().replace(hours=0, minutes=0, seconds=0)
                response_message = wit_client.run_actions()
                self.send_message(PAGE_ACCESS_TOKEN, sender, response_message)
        return HttpResponse()

    def messaging_events(self, entries):
        """Generate tuples of (sender_id, message_text) from the
        provided payload.
        """
        # data = json.loads(payload)
        messaging_events = entries["messaging"]
        for event in messaging_events:
            if "message" in event and "text" in event["message"]:
                yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
            else:
                yield event["sender"]["id"], "I can't echo this"

    def send_message(self, token, recipient, text):
        """Send the message text to recipient with id recipient.
        """

        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                          params={"access_token": token},
                          data=json.dumps({
                              "recipient": {"id": recipient},
                              "message": {"text": text.decode('unicode_escape')}
                          }),
                          headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print r.text
