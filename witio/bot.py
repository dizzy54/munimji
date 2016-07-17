from wit import Wit
import fb
from django.conf import settings


class MunimjiWitClient(Wit):
    """setup a wit client with actions
    """
    def _get_first_entity_value(entities, entity):
        value_list = entities[entity]
        if value_list:
            value = value_list[0]
            if value:
                return value
        return None

    # mandatory action, triggered at wit response
    def _send(self, request, response):
        context = request['context']
        session_id = request['session_id']
        text = response['text']
        recipient_id = context['_fbid_']

        if recipient_id:
            print 'send triggered with recipient id %s' % recipient_id
            print 'text = %s' % text
            fb.send_message(recipient_id, text)
        else:
            print('couldn\'t find user for session %s' % session_id)

    # custom actions
    def _set_split(self, request):
        print 'setSplit triggered'

        context = request['context']
        entities = request['entities']

        amount_of_money = self._get_first_entity_value(entities, 'amount_of_money')
        if amount_of_money:
            context['amount_split'] = amount_of_money
        else:
            context['amount_of_money'] = '0'
            context['amount_split'] = '0'

        return context

    def __init__(self):
        actions = {
            'send': self._send,
            'setSplit': self._set_split,
        }
        super(MunimjiWitClient, self).__init__(access_token=settings.WIT_ACCESS_TOKEN, actions=actions)
