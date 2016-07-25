import json
# import re
# from pprint import pprint
# import settings
from datetime import datetime
import traceback

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from requests_oauthlib import OAuth1Session

from witio.models import Session
import fb
# import witbot
from apiaibot import MyApiaiClient
from django.conf import settings
from users.models import RegisteredUser

PAGE_ACCESS_TOKEN = settings.PAGE_ACCESS_TOKEN
VERIFY_TOKEN = settings.VERIFY_TOKEN


class SplitwiseOauthRedirect(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            oauth_token = request.GET['oauth_token']
            oauth_verifier = request.GET['oauth_verifier']
            # print oauth_token
            # print oauth_verifier
            user = RegisteredUser.objects.get(resource_owner_key=oauth_token)
            user.oauth_verifier = oauth_verifier
            oauth = OAuth1Session(
                settings.SPLITWISE_CLIENT_KEY,
                client_secret=settings.SPLITWISE_CLIENT_SECRET,
                resource_owner_key=user.resource_owner_key,
                resource_owner_secret=user.resource_owner_secret,
                verifier=oauth_verifier
            )
            access_token_url = 'https://secure.splitwise.com/api/v3.0/get_access_token'
            oauth_tokens = oauth.fetch_access_token(access_token_url)
            user.splitwise_key = oauth_tokens.get('oauth_token')
            user.splitwise_secret = oauth_tokens.get('oauth_token_secret')
            user.save()
        except:
            traceback.print_exc()
        return redirect('https://www.messenger.com/t/munimbot')


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
        # print payload
        data = json.loads(payload)
        messaging_entries = data["entry"][0]
        if "messaging" in messaging_entries and "message" in messaging_entries["messaging"][0]:
            for sender, message, send_to_wit in self.messaging_events(messaging_entries):
                if send_to_wit:
                    print "Incoming from %s: %s" % (sender, message)
                    user_details = fb.get_user_details(sender)
                    now = datetime.now()
                    session_id = sender + str(now.year) + str(now.month) + str(now.day)
                    # print "length of session id = %s" % str(len(session_id))
                    try:
                        first_name = user_details['first_name']
                        last_name = user_details['last_name']
                    except KeyError:
                        print "user details not found for fbid %s" % sender
                    else:
                        session, created = Session.objects.get_or_create(
                            first_name=first_name,
                            last_name=last_name,
                            fbid=sender,
                            session_id=session_id,
                        )
                        if created:
                            session.register_user_with_fbid()
                        # !maybe add a check to see if fbid already in context
                        context = session.wit_context
                        context['_fbid_'] = sender
                        session.wit_context = context
                        session.save()
                        '''
                        # for wit implementation
                        wit_client = witbot.get_wit_client()
                        print "context = %s" % context
                        context = wit_client.run_actions(
                            session_id,
                            message,
                            context,
                        )
                        session.wit_context = context
                        '''
                        # for apiai implementation
                        bot = MyApiaiClient(session_id=session_id)
                        bot.process_text_query(message)
                        session.save()
                else:
                    # fb.send_message(sender, message)
                    pass
        return HttpResponse()

    def messaging_events(self, entries):
        """Generate tuples of (sender_id, message_text) from the
        provided payload.
        """
        # data = json.loads(payload)
        messaging_events = entries["messaging"]
        for event in messaging_events:
            if "message" in event and "text" in event["message"]:
                yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape'), True
            else:
                yield event["sender"]["id"], "I can't respond to this", False
