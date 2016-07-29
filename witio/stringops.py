# from collections import defaultdict
from itertools import groupby


def get_response_string_from_matched_names(name_response, payee=True):
    """ returns None if all names matched
    else returns a string to be sent to user explaining mismatches
    """
    print "entered response string function"
    matched_index_list, doubt_list, unmatched_entities_list, self_included = name_response
    
    entity = 'payee(s)'
    if not payee:
        entity = 'payer(s)'

    if not doubt_list and not unmatched_entities_list:
        print "all matched"
        return None

    elif doubt_list and not unmatched_entities_list:
        doubt_names = []
        for doubt in doubt_list:
            name_list = [entry[0] for entry in doubt]
            names = ' / '.join(name_list)
            doubt_names.append(names)
        doubt_names_string = ' and '.join(doubt_names)

        return_string = 'Sorry, but I have doubts between your friends %s for tagging as %s. Please answer the following question again.' %(
            doubt_names_string,
            entity
        )
        print "only doubt"
        return return_string

    elif not doubt_list and unmatched_entities_list:
        # for unmatched
        unmatched_names = []
        for name in unmatched_entities_list:
            unmatched_names.append(name)
        unmatched_names_string = ' and '.join(unmatched_names)
        unmatched_return_string = 'Sorry, I am unable to identify %s in your friends for tagging as %s. Please answer the following question again.' % (
            unmatched_names_string,
            entity
        )
        return_string = unmatched_return_string
        print "only unmatched"
        return return_string

    elif doubt_list and unmatched_entities_list:
        # for doubt string
        doubt_names = []
        for doubt in doubt_list:
            # print doubt
            name_list = [entry[0] for entry in doubt]
            names = ' / '.join(name_list)
            doubt_names.append(names)
        doubt_names_string = ' and '.join(doubt_names)
        doubt_return_string = 'Sorry, but I have doubts between your friends %s for tagging as %s. ' % (
            doubt_names_string, entity
        )

        # for unmatched
        unmatched_names = []
        for name in unmatched_entities_list:
            unmatched_names.append(name)
        unmatched_names_string = ' and '.join(unmatched_names)
        unmatched_return_string = 'Also, I am unable to identify %s in your friends for tagging as %s. Please answer the following questions again.' % (
            unmatched_names_string,
            entity
        )
        return_string = doubt_return_string + unmatched_return_string
        print "doubt and unmatched"
        return return_string

    else:
        print 'something is wrong. Hope you are checking your logs'

def match_from_name_list(entity, full_name_list, self_included=False):
    """ returns list of index of matching names, doubt cases and unmatched entities list
    """
    unmatched_names = entity.split()
    matched_list = []
    matched_index_list = []
    unmatched_entities_list = []
    doubt_list = []

    self_pronoun_list = ['me', 'i', 'myself']

    # remove consecutively same entities and self pronouns
    i = 0
    unmatched_names_updated = []
    for query_entity in unmatched_names:
        if query_entity.lower() in self_pronoun_list:
            self_included = True
        elif i == 0:
            unmatched_names_updated.append(query_entity)
        elif query_entity.lower() != unmatched_names[i - 1].lower():
            unmatched_names_updated.append(query_entity)
        i += 1

    for query_entity in unmatched_names_updated:
        matched_list.append([])
        i = 0
        for full_name in full_name_list:
            if query_entity.lower() in full_name.lower():
                # query matched with name
                matched_list[-1].append([full_name.lower(), i])
                # print matched_list
            i += 1

    # print unmatched_names_updated
    # print matched_list

    if not matched_list:
        unmatched_entities_list = unmatched_names_updated
        print unmatched_entities_list
        return matched_index_list, doubt_list, unmatched_entities_list, self_included
    # check if entire string is a name
    if matched_list[1:] == matched_list[:1]:
        # print "single name"
        full_names = matched_list[0]
        if full_names:
            if len(full_names) == 1:
                # print "1 word name (single) %s added" % str(full_names[0])
                matched_index_list.append(full_names[0])
            else:
                doubt_list.append(full_names)
        else:
            unmatched_entities_list = unmatched_names_updated

        matched_index_list, doubt_list = _remove_doubt_entries_if_confirmed(matched_index_list, doubt_list)
        return matched_index_list, doubt_list, unmatched_entities_list, self_included

    # check for 1 word names
    unmatched_2_word_names = []
    i = 0
    for query_entity in unmatched_names_updated:
        matched_full_names = matched_list[i]
        if len(matched_full_names) == 0:
            # no matches found for entity
            unmatched_entities_list.append(query_entity)
        elif len(unmatched_names_updated) > i + 1:
            # next entity exists
            next_entity_matches = matched_list[i + 1]
            # print 'i = %s' % str(matched_full_names)
            # print 'i + 1 = %s' % str(next_entity_matches)
            # find if names match any in next entity
            matched = False
            for name in matched_full_names:
                if name in next_entity_matches:
                    matched = True
            if not matched:
                # next entity does not contain same full name
                if unmatched_2_word_names and unmatched_2_word_names[-1][1][0] == query_entity:
                    # entity already added to unmatched_2_word_names
                    pass
                else:
                    # remove already added names
                    for matched_name in matched_index_list:
                        if matched_name in matched_full_names:
                            matched_full_names.remove(matched_name)

                    # add to matched or doubt list
                    if matched_full_names:
                        if len(matched_full_names) == 1:
                            print "1 word name %s added" % str(matched_full_names[0])
                            matched_index_list.append(matched_full_names[0])
                        else:
                            doubt_list.append(matched_full_names)
            else:
                # next entity contains matching full name
                print "entities added to 2 word names"
                unmatched_2_word_names.append([
                    [query_entity, matched_full_names],
                    [unmatched_names_updated[i + 1], next_entity_matches]
                ])
        else:
            # entity is last in list
            if unmatched_2_word_names and unmatched_2_word_names[-1][1][0] == query_entity:
                # entity already added to unmatched_2_word_names
                pass
            else:
                # remove already added names
                for matched_name in matched_index_list:
                    if matched_name in matched_full_names:
                        matched_full_names.remove(matched_name)

                # add to matched or doubt list
                if matched_full_names:
                    if len(matched_full_names) == 1:
                        print "1 word name %s added" % str(matched_full_names[0])
                        matched_index_list.append(matched_full_names[0])
                    else:
                        doubt_list.append(matched_full_names)
        i += 1

    # check for 2 word names
    unmatched_3_word_names = []

    if len(unmatched_2_word_names) == 0:
        matched_index_list, doubt_list = _remove_doubt_entries_if_confirmed(matched_index_list, doubt_list)
        return matched_index_list, doubt_list, unmatched_entities_list, self_included

    i = 0
    for entry1, entry2 in unmatched_2_word_names:
        if i != len(unmatched_2_word_names) - 1:
            # not the last entry
            entry3 = unmatched_2_word_names[i + 1][0]
            if entry2 == entry3:
                # consecutive same entries means 3 or more word name
                print "entities added to 3 word names"
                unmatched_3_word_names.append([entry1, entry2, unmatched_2_word_names[i + 1][1]])
            else:
                # 2 word name
                _process_entries([entry1, entry2], matched_index_list, doubt_list)
                '''
                common_full_names = set(entry1[1]).intersection(set(entry2[1]))
                # remove already added names
                for matched_name in matched_index_list:
                    if matched_name in common_full_names:
                        common_full_names.remove(matched_name)

                # add to matched or doubt list
                if common_full_names:
                    if len(common_full_names) == 1:
                        # only 1 common name, match it
                        print "2 word name %s added" % str(list(common_full_names)[0])
                        matched_index_list.append(list(common_full_names)[0])
                    else:
                        # multiple common names, add to doubt list
                        doubt_list.append(common_full_names)
                '''
        else:
            # last entry
            print "last 2 word entry entities - "
            if unmatched_3_word_names:
                print unmatched_3_word_names[-1]
                print entry1
                # print unmatched_3_word_names[-1][2]
                print entry2

            if (
                unmatched_3_word_names and
                unmatched_3_word_names[-1][1] == entry1 and
                unmatched_3_word_names[-1][2] == entry2
            ):
                print "last 2 word name already in 3 word list"
                # entry already exists in 3 word names
                pass
            else:
                _process_entries([entry1, entry2], matched_index_list, doubt_list)
                '''
                common_full_names = set(entry1[1]).intersection(set(entry2[1]))
                # remove already added names
                for matched_name in matched_index_list:
                    if matched_name in common_full_names:
                        common_full_names.remove(matched_name)

                # add to matched or doubt list
                if common_full_names:
                    if len(common_full_names) == 1:
                        # only 1 common name, match it
                        print "2 word name %s added" % str(list(common_full_names)[0])
                        matched_index_list.append(list(common_full_names)[0])
                    else:
                        # multiple common names, add to doubt list
                        doubt_list.append(common_full_names)
                '''
        i += 1

    # check for 3 word names
    # unmatched_remaining_names = []

    if len(unmatched_3_word_names) == 0:
        matched_index_list, doubt_list = _remove_doubt_entries_if_confirmed(matched_index_list, doubt_list)
        return matched_index_list, doubt_list, unmatched_entities_list, self_included

    # i = 0
    for entry1, entry2, entry3 in unmatched_3_word_names:
        # 3 word name
        _process_entries([entry1, entry2, entry3], matched_index_list, doubt_list)
        '''
        common_full_names = set(entry1[1]).intersection(set(entry2[1])).intersection(set(entry3[1]))
        if len(common_full_names) == 1:
            # only 1 common name, match it
            print "3 word name %s added" % str(list(common_full_names)[0])
            matched_index_list.append(list(common_full_names)[0])
        else:
            # multiple common names, add to doubt list
            doubt_list.append(list(common_full_names))
        # i += 1
        '''
    matched_index_list, doubt_list = _remove_doubt_entries_if_confirmed(matched_index_list, doubt_list)
    return matched_index_list, doubt_list, unmatched_entities_list, self_included


def _remove_doubt_entries_if_confirmed(confirmed_list, doubt_list):
    new_confirmed_list = list(confirmed_list)
    doubt_list = [k for k, v in groupby(sorted(doubt_list))]  # to remove duplicates
    new_doubt_list = []
    for doubt_entry in doubt_list:
        new_doubt_entry = []
        for name_entry in doubt_entry:
            if not (name_entry in new_confirmed_list):
                new_doubt_entry.append(name_entry)
        if len(new_doubt_entry) == 0:
            pass
        elif len(new_doubt_entry) == 1:
            new_confirmed_list.append(new_doubt_entry[0])
        else:
            new_doubt_list.append(new_doubt_entry)
    return new_confirmed_list, new_doubt_list


def _process_entries(entry_list, matched_index_list, doubt_list):
    # note - doesn't handle possibility of 2 words matching in 2 consecutive 3 word entries
    new_entry_list = list(entry_list)
    i = 0
    for entry in entry_list:
        for name in entry[1]:
            if name in matched_index_list:
                new_entry_list[i][1].remove(name)
        i += 1

    common_full_names = intersect([entry[1] for entry in new_entry_list])

    # if no common full names, check individual entities singly
    if len(common_full_names) == 0:
        for entry in new_entry_list:
            entry[1] = [name for name in entry[1] if name not in matched_index_list]
            if len(entry[1]) == 1:
                print "1 word name %s added" % str(entry[1][0])
                matched_index_list.append(entry[1][0])
            else:
                doubt_list.append(entry[1])
    elif len(common_full_names) == 1:
        # only 1 common name, match it
        print "%s word name %s added" % (str(len(entry_list)), str(list(common_full_names)[0]))
        matched_index_list.append(list(common_full_names)[0])
    else:
        # multiple common names, add to doubt list
        doubt_list.append(list(common_full_names))


def intersect(lists):
    return list(set.intersection(*map(set, lists)))
