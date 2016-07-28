# from collections import defaultdict


def match_from_name_list(entity, full_name_list):
    """ returns list of index of matching names, doubt cases and unmatched entities list
    """
    unmatched_names = entity.split()
    matched_list = []
    matched_index_list = []
    unmatched_entities_list = []
    doubt_list = []

    # remove consecutively same entities
    i = 0
    unmatched_names_updated = []
    for query_entity in unmatched_names:
        if i == 0:
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
                matched_list[-1].append((full_name.lower(), i))
                # print matched_list
            i += 1

    print unmatched_names_updated
    print matched_list

    # check if entire string is a name
    if matched_list[1:] == matched_list[:1]:
        print "single name"
        full_names = matched_list[0]
        if full_names:
            if len(full_names) == 1:
                print "1 word name (single) %s added" % str(full_names[0])
                matched_index_list.append(full_names[0])
            else:
                doubt_list.append(full_names)
        else:
            unmatched_entities_list = unmatched_names_updated

        return matched_index_list, doubt_list, unmatched_entities_list

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
                    if len(matched_full_names) == 1:
                        print "1 word name %s added" % str(matched_full_names[0])
                        matched_index_list.append(matched_full_names[0])
                    else:
                        doubt_list.append(matched_full_names)
            else:
                # next entity contains matching full name
                print "entities added to 2 word names"
                unmatched_2_word_names.append((
                    (query_entity, matched_full_names),
                    (unmatched_names_updated[i + 1], next_entity_matches)
                ))
        else:
            # entity is last in list
            if unmatched_2_word_names and unmatched_2_word_names[-1][1][0] == query_entity:
                # entity already added to unmatched_2_word_names
                pass
            else:
                if len(matched_full_names) == 1:
                    print "1 word name %s added" % str(matched_full_names[0])
                    matched_index_list.append(matched_full_names[0])
                else:
                    doubt_list.append(matched_full_names)
        i += 1

    # check for 2 word names
    unmatched_3_word_names = []

    if len(unmatched_2_word_names) == 0:
        return matched_index_list, doubt_list, unmatched_entities_list

    i = 0
    for entry1, entry2 in unmatched_2_word_names:
        if i != len(unmatched_2_word_names) - 1:
            # not the last entry
            entry3 = unmatched_2_word_names[i + 1][0]
            if entry2 == entry3:
                # consecutive same entries means 3 or more word name
                print "entities added to 3 word names"
                unmatched_3_word_names.append((entry1, entry2, unmatched_2_word_names[i + 1][1]))
            else:
                # 2 word name
                common_full_names = set(entry1[1]).intersection(set(entry2[1]))
                if len(common_full_names) == 1:
                    # only 1 common name, match it
                    print "2 word name %s added" % str(list(common_full_names)[0])
                    matched_index_list.append(list(common_full_names)[0])
                else:
                    # multiple common names, add to doubt list
                    doubt_list.append(common_full_names)
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
                common_full_names = set(entry1[1]).intersection(set(entry2[1]))
                if len(common_full_names) == 1:
                    # only 1 common name, match it
                    print "2 word name %s added" % str(list(common_full_names)[0])
                    matched_index_list.append(list(common_full_names)[0])
                else:
                    # multiple common names, add to doubt list
                    doubt_list.append(common_full_names)
        i += 1

    # check for 3 word names
    # unmatched_remaining_names = []

    if len(unmatched_3_word_names) == 0:
        return matched_index_list, doubt_list, unmatched_entities_list

    # i = 0
    for entry1, entry2, entry3 in unmatched_3_word_names:
        # 3 word name
        common_full_names = set(entry1[1]).intersection(set(entry2[1])).intersection(set(entry3[1]))
        if len(common_full_names) == 1:
            # only 1 common name, match it
            print "3 word name %s added" % str(list(common_full_names)[0])
            matched_index_list.append(list(common_full_names)[0])
        else:
            # multiple common names, add to doubt list
            doubt_list.append(list(common_full_names))
        # i += 1
    return matched_index_list, doubt_list, unmatched_entities_list
