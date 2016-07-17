import json
# import re
# from pprint import pprint
# import settings
from datetime import datetime

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from users.models import Session
import fb
import bot
from django.conf import settings

PAGE_ACCESS_TOKEN = settings.PAGE_ACCESS_TOKEN
VERIFY_TOKEN = settings.VERIFY_TOKEN


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
            for sender, message in self.messaging_events(messaging_entries):
                print "Incoming from %s: %s" % (sender, message)
                user_details = fb.get_user_details(sender)
                session_id = sender + datetime.now().replace(hours=0, minutes=0, seconds=0)
                user, created = Session.object.get_or_create(
                    first_name=user_details['first_name'],
                    last_name=user_details['last_name'],
                    fbid=sender,
                    session_id=session_id,
                )
                # !maybe add a check to see if fbid already in context
                context = user.wit_context
                context['_fbid_'] = sender
                user.wit_context = context
                user.save()
                text = message.text
                if message.attachments:
                    fb.send_message(sender, 'Sorry I can only process text messages for now.')
                elif text:
                    wit_client = bot.MunimjiWitClient()
                    wit_client.run_actions(
                        session_id,
                        text,
                        context,
                    )
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
