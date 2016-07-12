import json
import requests
# import re
# from pprint import pprint
# import settings

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = "EAARlALJSWxoBANm5ybZAzd45BkXZCxZAr6bBZAiHXXdVVwYv4T6wmmII5X0aXUxqMgCQsC2Dshd8gCcYflZAAekFnsBGW2BVvC86w7aaRkzeNGgWn85V3iXb52GZChSsOZBBZCJYK790AaL5kAj2rvO4x5UW4iPmn2hBuZCeyZBB6KVgZDZD"
VERIFY_TOKEN = "2550036"


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
        payload = request.get_data()
        print payload
        for sender, message in self.messaging_events(payload):
            print "Incoming from %s: %s" % (sender, message)
            self.send_message(PAGE_ACCESS_TOKEN, sender, message)

    def messaging_events(payload):
        """Generate tuples of (sender_id, message_text) from the
        provided payload.
        """
        data = json.loads(payload)
        messaging_events = data["entry"][0]["messaging"]
        for event in messaging_events:
            if "message" in event and "text" in event["message"]:
                yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
            else:
                yield event["sender"]["id"], "I can't echo this"

    def send_message(token, recipient, text):
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
