import requests
import json
from django.conf import settings


def send_message(recipient, text, quick_replies=None, token=settings.PAGE_ACCESS_TOKEN):
        """Send the message text to recipient with id recipient.
        """
        if text:
            if quick_replies and isinstance(quick_replies, list):
                quick_replies_r = [{
                    'content_type': 'text',
                    'title': q_text,
                    'payload': q_text
                } for q_text in quick_replies]
                r = requests.post(
                    "https://graph.facebook.com/v2.6/me/messages",
                    params={"access_token": token},
                    data=json.dumps({
                        "recipient": {"id": recipient},
                        "message": {
                            "text": text.decode('unicode_escape'),
                            "quick_replies": quick_replies_r
                        }
                    }),
                    headers={'Content-type': 'application/json'}
                )
            else:
                r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                                  params={"access_token": token},
                                  data=json.dumps({
                                      "recipient": {"id": recipient},
                                      "message": {"text": text.decode('unicode_escape')}
                                  }),
                                  headers={'Content-type': 'application/json'})
            if r.status_code != requests.codes.ok:
                print "request not ok - " + str(r.text)
        else:
            print "empty message"


def get_user_details(fbid, token=settings.PAGE_ACCESS_TOKEN):
    """Get user details from facebook graph api
    """
    user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    user_details_params = {'fields': 'first_name, last_name', 'access_token': token}
    return requests.get(user_details_url, user_details_params).json()
