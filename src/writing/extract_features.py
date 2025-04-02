# coding=utf-8
import json
import re

from .models import WritingRecord

def decide_edition_range(prev_article, cur_article):
    """ Return s1, e1, s2, e2 (the position after the edition).
    Note that each time, we only insert at most one character (because of the keyinput event listener).

    common substring prev_article[0:s1] == cur_article[0:s2] and prev_article[e1:] == cur_article[e2:]
    that is s1 == s2, and len(prev_article)-e1 == len(cur_article)-e2
    Different edition examples:
        without selection:
            
            insert means s1 == e1 and s2+1 == e2
            delete means s1+1 == e1 and s2 == e2

            'abcd|' -> 'abcde|' insert at the end, s1 == 4 and e1 == 4 and s2 == 4 and e2 == 5
            'abcd|' -> 'abc|' delete at the end, s1 == 3 and e1 == 4 and s2 == 3 and e2 == 3
            '|abcd' -> 'e|abcd' insert at the beginning, s1 == 0 and e1 == 0 and s2 == 0 and e2 == 1
            'a|bcd' -> '|bcd' delete at the beginning, s1 == 0 and e1 == 1 and s2 == 0 and e2 == 0
            'abc|d' -> 'abce|d' insert in the middle, s1 == 3 and e1 == 3 and s2 == 3 and e2 == 4
            'abc|d' -> 'ab|d' delete in the middle, s1 == 2 and e1 == 3 and s2 == 2 and e2 == 2
        with selection:
            
            insert means s2+1 == e2
            delete means s2 == e2

            'ab|cd|' -> 'abe|' select and insert at the end, s1 == 2 and e1 == 4 and s2 == 2 and e2 == 3
            'ab|cd|' -> 'ab|' select and delete at the end, s1 == 2 and e1 == 4 and s2 == 2 and e2 == 2
            'a|bc|d' -> 'ae|d' select and insert in the middle, s1 == 1 and e1 == 3 and s2 == 1 and e2 == 2
            'a|bc|d' -> 'a|d' select and delete in the middle, s1 == 1 and e1 == 3 and s2 == 1 and e2 == 1
            '|ab|cd' -> 'e|cd' select and insert at the beginning, s1 == 0 and e1 == 2 and s2 == 0 and e2 == 1
            '|ab|cd' -> '|cd' select and delete at the beginning, s1 == 0 and e1 == 2 and s2 == 0 and e2 == 0
        special cases:
            'a|bc|d' -> 'ac|d' select and insert one same char in the middle, check the inputtype if it's delete or insert. 
                            This current implementation considers it as deleting b without selection.
            'a|c|d' -> 'ac|d' s1 = e1 = s2 = e2 = 3. Currently considered as deleting with selection.
    """
    s1 = s2 = e1 = e2 = -1

    if prev_article is None or len(prev_article) == 0:
        # start from the scratch
        s1 = e1 = s2 = 0
        e2 = len(cur_article)
        return s1, e1, s2, e2
    else:
        # because the edition is continuous, so we only need to find the first and second different positions.
        prev_i = cur_i = 0
        while prev_i < len(prev_article) and cur_i < len(cur_article):
            prev_char = prev_article[prev_i]
            cur_char = cur_article[cur_i]

            if prev_char != cur_char:
                if s1 == -1:
                    s1 = prev_i
                    s2 = cur_i
                    break
            prev_i += 1
            cur_i += 1

        if s1 == -1:
            s1 = s2 = prev_i  # prev_i == cur_i == min(len(prev_article), len(cur_article))
        
        if s1 == len(prev_article) or s2 == len(cur_article):
            e1 = len(prev_article)
            e2 = len(cur_article)

            assert prev_article[0:s1] == cur_article[0:s2] and prev_article[e1:] == cur_article[e2:]
            assert s1 == s2 and len(prev_article)-e1 == len(cur_article)-e2
            return s1, e1, s2, e2

        # now we know prev_article[0:s1] == cur_article[0:s2]
        # so we need to find e1 and e2 st prev_article[e1:] == cur_article[e2:]
        # Note that cur_articel can be considered as 
        #   1) deleting a substring (empty or the whole string) from prev_article
        #   2) (optional) add ONE char at s2
        # So we can try to find the common suffix e1 and e2 in prev_article[s1:] and cur_article[s2:] (for delete) or cur_article[s2+1:] (for insertion)
        prev_i = len(prev_article) - 1
        cur_i = len(cur_article) - 1
        while prev_i >= s1 and cur_i >= s2:
            prev_char = prev_article[prev_i]
            cur_char = cur_article[cur_i]

            if prev_char != cur_char:
                if e1 == -1:
                    e1 = prev_i + 1
                    e2 = cur_i + 1
                    break
            prev_i -= 1
            cur_i -= 1

        if e1 == -1:
            e1 = prev_i + 1
            e2 = cur_i + 1
        
        assert prev_article[0:s1] == cur_article[0:s2] and prev_article[e1:] == cur_article[e2:]
        assert s1 == s2 and len(prev_article)-e1 == len(cur_article)-e2
        return s1, e1, s2, e2

        
def test_decide_edition_range():
    s1, e1, s2, e2 = decide_edition_range('abcd', 'abcde')
    print(s1, e1, s2, e2)
    assert s1 == 4 and e1 == 4 and s2 == 4 and e2 == 5
    s1, e1, s2, e2 = decide_edition_range('abcd', 'abc')
    print(s1, e1, s2, e2)
    assert s1 == 3 and e1 == 4 and s2 == 3 and e2 == 3

    s1, e1, s2, e2 = decide_edition_range('abcd', 'eabcd')
    print(s1, e1, s2, e2)
    assert s1 == 0 and e1 == 0 and s2 == 0 and e2 == 1

    s1, e1, s2, e2 = decide_edition_range('abcd', 'bcd')
    print(s1, e1, s2, e2)
    assert s1 == 0 and e1 == 1 and s2 == 0 and e2 == 0

    s1, e1, s2, e2 = decide_edition_range('abcd', 'abced')
    print(s1, e1, s2, e2)
    assert s1 == 3 and e1 == 3 and s2 == 3 and e2 == 4

    s1, e1, s2, e2 = decide_edition_range('abcd', 'abd')
    print(s1, e1, s2, e2)
    assert s1 == 2 and e1 == 3 and s2 == 2 and e2 == 2

    s1, e1, s2, e2 = decide_edition_range('abcd', 'abe')
    print(s1, e1, s2, e2)
    assert s1 == 2 and e1 == 4 and s2 == 2 and e2 == 3

    s1, e1, s2, e2 = decide_edition_range('abcd', 'ab')
    print(s1, e1, s2, e2)
    assert s1 == 2 and e1 == 4 and s2 == 2 and e2 == 2

    s1, e1, s2, e2 = decide_edition_range('abcd', 'aed')
    print(s1, e1, s2, e2)
    assert s1 == 1 and e1 == 3 and s2 == 1 and e2 == 2

    s1, e1, s2, e2 = decide_edition_range('abcd', 'ad')
    print(s1, e1, s2, e2)
    assert s1 == 1 and e1 == 3 and s2 == 1 and e2 == 1

    s1, e1, s2, e2 = decide_edition_range('abcd', 'ecd')
    print(s1, e1, s2, e2)
    assert s1 == 0 and e1 == 2 and s2 == 0 and e2 == 1

    s1, e1, s2, e2 = decide_edition_range('abcd', 'cd')
    print(s1, e1, s2, e2)
    assert s1 == 0 and e1 == 2 and s2 == 0 and e2 == 0

    s1, e1, s2, e2 = decide_edition_range('acd', 'acd')
    print(s1, e1, s2, e2)
    assert s1 == 3 and e1 == 3 and s2 == 3 and e2 == 3
    

def decide_operation_type(s1, e1, s2, e2):
    op_type = 'unknown'
    is_selection = 'unknown'

    if s1 == e1 == s2 == e2:
        # 'a|c|d' -> 'ac|d' s1 = e1 = s2 = e2 = 3.
        op_type = 'same'
        is_selection = True
        return op_type, is_selection

    if s2+1 == e2:
        op_type = 'insert'
        is_selection = not (s1 == e1)
    elif s2 == e2:
        op_type = 'delete'
        is_selection = not (s1+1 == e1)
    else:
        raise AssertionError('unkown situation')
    return op_type, is_selection


def count_num_of_words(article):
    return len([x for x in re.split(r'[,.?!;:\s]\s*', article) if len(x)>0])


def count_num_of_deleted_words(deletion, preceding_content, subsequent_content):
    sep = ' \t\n\r\f\v' + ',.?!;:'
    subtraction = 0
    if deletion[0] not in sep:
        # the first deleted word may not be complete
        if not preceding_content:
            # preceding_content is empty
            # the first deleted word is at the beginning of the text,
            # so it's complete
            pass
        else:
            if preceding_content[-1] not in sep:
                # the first deleted word is not complete
                subtraction += 1
    if deletion[-1] not in sep:
        # the last may not be complete
        if not subsequent_content:
            pass
        else:
            if subsequent_content[0] not in sep:
                subtraction += 1

    return max(count_num_of_words(deletion)-subtraction, 0)


def count_num_of_inserted_words(insertion, preceding_content, subsequent_content):
    # we currently manually use a space. It might add 1 to the num of inserted words.
    subsequent_content = ' '
    return count_num_of_deleted_words(insertion, preceding_content, subsequent_content)


def count_num_of_jump_words(content, preceding_content, subsequent_content):
    if not content:
        return 0
    return count_num_of_deleted_words(content, preceding_content, subsequent_content)


def extract_features(writing_record):
    if not writing_record.record:
        return None

    score = writing_record.score
    record = json.loads(writing_record.record)
    article = writing_record.article
    start_time = record['startTime']
    event_sequence = record['sequences']
    submit_time = record['submitTime']
    # num_of_words = len(article.split())
    num_of_words = count_num_of_words(article)

    if len(event_sequence) > 0:
        planning_time = event_sequence[0]['time'] - start_time
    
    writing_time = submit_time - event_sequence[0]['time']

    within_a_word_pause_list = []
    between_words_pause_list =[]
    between_paragraphs_pause_list = []
    between_sentences_pause_list = []

    last_in_word_timestamp = None
    last_between_word_timestamp = None
    last_paragraph_timestamp = None
    last_sentence_timestamp = None

    sequential_deleted_content = ''
    sequential_deletion_length_list = []
    preceding_deletion_content = ''
    subsequent_deletion_content = ''
    sequential_deletion_time = None
    sequential_deletion_time_list = []

    # sequential insertion means typing without pausing more than 2s (2000ms)
    sequential_inserted_content = ''
    sequential_insertion_length_list = []
    preceding_insertion_content = ''
    subsequent_insertion_content = ''
    sequential_insertion_time = None
    sequential_insertion_time_list = []

    jump_length_list = []
    jump_time_list = []

    last_position = -1  # if last edition includes selection, it points to the end of the selection.
    prev_article = ''
    pre_sequential_char_insertion_timestamp = None

    def handle_insertion():
        nonlocal sequential_deleted_content
        nonlocal sequential_deletion_time
        nonlocal last_in_word_timestamp
        nonlocal last_between_word_timestamp
        nonlocal last_paragraph_timestamp
        nonlocal last_sentence_timestamp
        nonlocal pre_sequential_char_insertion_timestamp
        nonlocal sequential_inserted_content
        nonlocal sequential_insertion_time
        nonlocal preceding_insertion_content
        nonlocal subsequent_insertion_content

        if sequential_deleted_content:
            sequential_deletion_length_list.append(count_num_of_deleted_words(sequential_deleted_content, preceding_deletion_content, subsequent_deletion_content))
            sequential_deletion_time_list.append(timestamp-sequential_deletion_time)
        sequential_deleted_content = ''  # reset the deletion
        sequential_deletion_time = None

        if current_position != last_position+1:
            # The editing position is not continuous
            last_in_word_timestamp = None
            last_between_word_timestamp = None
            last_paragraph_timestamp = None
            last_sentence_timestamp = None
            pre_sequential_char_insertion_timestamp = None

            sequential_inserted_content = ''
            sequential_insertion_time = None

            # handle jump edition
            if current_position < last_position:
                jump_length_list.append(count_num_of_jump_words(
                    prev_article[end1:last_position+1],
                    prev_article[:end1],
                    prev_article[last_position+1:]
                ))
                jump_time_list.append(timestamp-prev_timestamp)
            
        else:
            # only record sequential insertion when it's a continuous insertion and a long pause
            if is_long_pause:
                # end of a typing chunk so record it
                if sequential_inserted_content:
                    subsequent_insertion_content = prev_article[end1:]  # only the latest subsequent content matters.
                    sequential_insertion_length_list.append(count_num_of_inserted_words(sequential_inserted_content, preceding_insertion_content, subsequent_insertion_content))
                    sequential_insertion_time_list.append(timestamp-sequential_insertion_time)
                # start a new typing chunk
                sequential_inserted_content = cur_content
                sequential_insertion_time = timestamp
                preceding_insertion_content = prev_article[:start1]
                
            else:
                if sequential_inserted_content:
                    # within a typing chunk, so append the inserted content
                    sequential_inserted_content = sequential_inserted_content + cur_content            

        if cur_content == ' ':
            # begin a new word (usually for between in word pause)
            last_in_word_timestamp = None
        elif cur_content in ',.?!;:':
            # separated by punctuation
            last_in_word_timestamp = None
            last_between_word_timestamp = None
            last_paragraph_timestamp = None
            if last_sentence_timestamp is None and pre_sequential_char_insertion_timestamp is not None:
                # assert pre_sequential_char_insertion_timestamp is not None
                last_sentence_timestamp = pre_sequential_char_insertion_timestamp
        elif cur_content == '\n':
            # begin a new paragraph
            last_in_word_timestamp = None
            last_between_word_timestamp = None
            last_sentence_timestamp = None
            # find the most recent non-enter input
            if last_paragraph_timestamp is None and pre_sequential_char_insertion_timestamp is not None:
                # assert pre_sequential_char_insertion_timestamp is not None
                last_paragraph_timestamp = pre_sequential_char_insertion_timestamp or timestamp                      
        else:
            # within a word
            if last_in_word_timestamp is not None:
                # within a word
                within_a_word_pause_list.append(timestamp-last_in_word_timestamp)
                last_sentence_timestamp = None
                last_paragraph_timestamp = None
            else:
                # start a new word, compute the between in word pause for continouse edition
                if last_between_word_timestamp is not None:
                    assert last_sentence_timestamp is None
                    assert last_paragraph_timestamp is None
                    between_words_pause_list.append(timestamp-last_between_word_timestamp)

                if last_sentence_timestamp is not None:
                    assert last_between_word_timestamp is None
                    between_sentences_pause_list.append(timestamp-last_sentence_timestamp)
                    last_sentence_timestamp = None

                if last_paragraph_timestamp is not None:
                    assert last_between_word_timestamp is None
                    between_paragraphs_pause_list.append(timestamp-last_paragraph_timestamp)
                    last_paragraph_timestamp = None

            last_in_word_timestamp = timestamp
            last_between_word_timestamp = timestamp
            pre_sequential_char_insertion_timestamp = timestamp

    def handle_deletion():
        nonlocal sequential_deleted_content
        nonlocal preceding_deletion_content
        nonlocal subsequent_deletion_content
        nonlocal sequential_deletion_time
        nonlocal sequential_inserted_content
        nonlocal sequential_insertion_time

        # reset them because this is not a sequential insertion
        sequential_inserted_content = ''
        sequential_insertion_time = None

        # handle jump edition
        if current_position < last_position:
            jump_length_list.append(count_num_of_jump_words(
                prev_article[end1:last_position+1],
                prev_article[:end1],
                prev_article[last_position+1:]
            ))
            jump_time_list.append(timestamp-prev_timestamp)

        if sequential_deleted_content == '':
            # this is a new deletion
            preceding_deletion_content = prev_article[:start1]
            subsequent_deletion_content = prev_article[end1:]
            sequential_deletion_time = timestamp

        if start1 == last_position+1:
            # delete the subsequent selection
            sequential_deleted_content = sequential_deleted_content + prev_content
        elif end1 == last_position+1:
            # delete the preceding selection
            sequential_deleted_content = prev_content + sequential_deleted_content
        else:
            # delete another selection
            if sequential_deleted_content:
                sequential_deletion_length_list.append(count_num_of_deleted_words(sequential_deleted_content, preceding_deletion_content, subsequent_deletion_content))
                sequential_deletion_time_list.append(timestamp-sequential_deletion_time)
            sequential_deleted_content = prev_content
            sequential_deletion_time = timestamp

    for event_i, event in enumerate(event_sequence):
        # print(event)
        # current_position = event['position']  # this is not accurate, use end2-1.
        input_type = event['inputType']
        data = event['data']
        timestamp = event['time']
        cur_article = event['article']

        start1, end1, start2, end2 = decide_edition_range(prev_article, cur_article)
        current_position = end2-1  # this is the last char index if it's positive, this can be -1 if deleting the prefix

        # print(start1, end1, start2, end2)
        # print(current_position, end2-1, decide_operation_type(start1, end1, start2, end2), data)
        # print(prev_article[start1:end1], '=>', 'newline' if cur_article[start2:end2] == '\n' else cur_article[start2:end2])

        op_type, is_selection = decide_operation_type(start1, end1, start2, end2)
        prev_content = prev_article[start1:end1]
        cur_content = cur_article[start2:end2]

        if event_i > 0:
            prev_timestamp = event_sequence[event_i-1]['time']
        else:
            prev_timestamp = timestamp

        is_long_pause = (timestamp-prev_timestamp) >= 2000

        # everything with selection are not within a word
        if is_selection:
            # The editing with selection is not continuous
            last_in_word_timestamp = None
            last_between_word_timestamp = None
            last_paragraph_timestamp = None
            last_sentence_timestamp = None
            pre_sequential_char_insertion_timestamp = None
            sequential_inserted_content = ''
            sequential_insertion_time = None

            if op_type == 'insert':
                handle_insertion()
            elif op_type == 'delete':
                handle_deletion()
            else:
                raise NotImplementedError(f'This [{op_type}] has not been supported yet')
        else:
            if op_type == 'insert':
                handle_insertion()
            elif op_type == 'delete':
                # It's not insertion operation
                last_in_word_timestamp = None
                last_between_word_timestamp = None
                last_paragraph_timestamp = None
                last_sentence_timestamp = None
                pre_sequential_char_insertion_timestamp = None

                handle_deletion()
            else:
                raise NotImplementedError(f'This [{op_type}] has not been supported yet')


        prev_article = cur_article
        last_position = current_position

    # print(len(within_a_word_pause_list), within_a_word_pause_list)
    # print(len(between_words_pause_list), between_words_pause_list)

    # print('planning_time', planning_time)
    # print('writing_time', writing_time)

    # only keep the results whose deletion length > 0.
    sequential_deletion_time_list = [t for t, l in zip(sequential_deletion_time_list, sequential_deletion_length_list) if l > 0]
    sequential_deletion_length_list = [x for x in sequential_deletion_length_list if x > 0]
    sequential_insertion_time_list = [t for t, l in zip(sequential_insertion_time_list, sequential_insertion_length_list) if l > 0]
    sequential_insertion_length_list = [x for x in sequential_insertion_length_list if x > 0]
    jump_time_list = [t for t, l in zip(jump_time_list, jump_length_list) if l > 0]
    jump_length_list = [x for x in jump_length_list if x > 0]

    features_dict = {
        'score':    score,
        'tottime':  writing_time,
        'platime':  planning_time,
        'numword':  num_of_words,
        'witpau':   within_a_word_pause_list,
        'bewpau':   between_words_pause_list,
        'parpau':   between_paragraphs_pause_list,
        'senpau':   between_sentences_pause_list,
        'dellen':   sequential_deletion_length_list,
        'deltime':  sequential_deletion_time_list,
        'numchun':  len(sequential_insertion_length_list),
        'chuword':  sequential_insertion_length_list,
        'chutime':  sequential_insertion_time_list,
        'numjump':  len(jump_time_list),
        'jumptime': jump_time_list,
        'jumpword': jump_length_list,
    }
    return features_dict


def main():
    # writing_record = WritingRecord.objects.get(pk=29)
    # print(writing_record.user)
    # extract_features(writing_record)
    # return
    for writing_record in WritingRecord.objects.all():
        if writing_record.user.username.startswith('litest'):
            continue
        try:
            features = extract_features(writing_record)
        except Exception as e:
            print(writing_record.user)
            print(e)
            
        # print(features)
        # return
        # writing_record.features = json.dumps(features)
        # writing_record.save()