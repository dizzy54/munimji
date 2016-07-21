from wit import Wit
import fb
from django.conf import settings


def get_first_entity_value(entities, entity):
    if entity in entities:
        value_list = entities[entity]
        value_first = value_list[0]
        if 'value' in value_first:
            return value_first['value']
    return None


def get_all_entity_values(entities, entity):
    if entity in entities:
        value_holder = entities[entity]
        value_list = []
        for entry in value_holder:
            if 'value' in entry:
                value_list.append(entry['value'])
        return value_list
    return None


def get_all_entity_values_as_string(entities, entity):
    value_list = get_all_entity_values(entities, entity)
    if value_list:
        list_string = ', '.join(value_list)
        if len(value_list) > 1:
            last_value = value_list[-1]
            last_value_length = len(last_value)
            list_string = list_string[:-(last_value_length + 1)] + ' and ' + last_value
        return list_string
    else:
        return None


# mandatory action, triggered at wit response
def _send(request, response):
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
def _set_split(request):
    print 'setSplit triggered'

    context = request['context']
    entities = request['entities']

    amount_of_money = get_first_entity_value(entities, 'amount_of_money')
    payers = get_all_entity_values_as_string(entities, 'payer')
    payees = get_all_entity_values_as_string(entities, 'payee')

    if amount_of_money and payers and payees:
        print "payers = " + payers
        print "payees = " + payees
        context['amount_split'] = amount_of_money / len(get_all_entity_values(entities, 'payee'))
        context['payer_string'] = payers
        context['payee_string'] = payees
    elif not payers:
        context['missing_payer'] = True
        if context.get('missing_payee'):
            del context['missing_payee']
        if context.get('missing_amount_of_money'):
            del context['missing_amount_of_money']
    elif not amount_of_money:
        context['missing_amount_of_money'] = True
        if context.get('missing_payer'):
            del context['missing_payer']
        if context.get('missing_payee'):
            del context['missing_payee']
    elif not payees:
        context['missing_payee'] = True
        if context.get('missing_payer'):
            del context['missing_payer']
        if context.get('missing_amount_of_money'):
            del context['missing_amount_of_money']
    else:
        context['amount_of_money'] = '0'
        context['amount_split'] = '0'

    return context


def _add_friend(request):
    print 'addFriend triggered'
    pass


def get_wit_client():
    """
    returns a custom wit client
    """
    actions = {
        'send': _send,
        'setSplit': _set_split,
    }
    return Wit(access_token=settings.WIT_ACCESS_TOKEN, actions=actions)
