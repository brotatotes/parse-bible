from books_of_the_bible import *
from format import BibleBook, BibleChapterAndVerses, BibleVerse, BibleText
from parse_dictionary import parse_dictionary
import re
import os
import json
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

porterStemmer = PorterStemmer()

def is_long_tag(text):
    return re.match(r'^<\$.*?\$.*?>$', text) != None

def is_tag(text):
    return re.match(r'^<.+?>$', text) != None

def get_opening_tag(text):
    match = re.match(r'^<([^/]+?)>$', text)
    if not match:
        return None
    else:
        return match.group(1)

def get_closing_tag(text):
    match = re.match(r'^</(.+?)>$', text)
    if not match:
        return None
    else:
        return match.group(1)

def is_verse_ref(text):
    return re.match(r'^{{\d+::\d+}}\d+<T>$', text) != None

def is_verse_text(text):
    return re.match(r'^[^<>]+$', text.replace('<\\>', '').replace('</>', '')) != None

def is_strongs_tag(text):
    return re.match(r'^</?M[^>]+>$', text) != None

def get_strongs_tag(text):
    if not is_strongs_tag(text): 
        raise Exception(f"Not a strongs tag: {text}")
    
    return re.search(r'M([^>]+)', text).group(1)

def is_sub_head(text):
    return re.match(r'^<S[SH]>.+</S[SH]>$', text) != None

def replace_tags(text):
    text = re.sub(r'<\\>', '<small>', text)
    text = re.sub(r'</>', '</small>', text)
    text = re.sub(r'{', '<em>', text)
    text = re.sub(r'}', '</em>', text)
    text = re.sub(r'<B>', '<strong>', text)
    text = re.sub(r'</B>', '</strong>', text)
    text = re.sub(r'<PM>', '<br><br>', text)
    text = re.sub(r'<PO>', '<br>', text)
    text = re.sub(r'<PN>', '<br>', text)
    text = re.sub(r'<PR>', '<br><br>', text)
    text = re.sub(r'<A>', '<br><br>', text)
    return text

def verse_ref_to_tags(text):    
    return re.sub(r'{{(\d+)::(\d+)}}(\d+)<T>', r'<verse_ref><book>\1</book><chapter>\2</chapter><verse>\3</verse></verse_ref>^', text)

def strongs_ref_to_tags(text):
    text = re.sub(r'(<M[GH][^>]+?>)(</small>)', r'\2\1', text)
    return re.sub(r'([^\^—\-.;,\s\u201c\u2018"]+)<(M[GH][^>]+?)>', r'<\2>\1</\2>', text)

def remove_continuing_quotes(text):
    return re.sub(r'[\+-][“‘]', '', text)

def combine_strongs_tags(text):
    text = re.sub(r'</(M[GH][^>]+?)>(\s+)<\1>', r'\2', text)
    return text

def remove_all_tags(text):
    text = re.sub(r'<[^>]*>', '', text)
    return text

def remove_unwanted_tags(text):
    tag_regs_to_keep = [
        r'M[^>]+',
        r'em',
        # r'strong', # bold is only ever used to bold first letter of sentences.
        r'small',
        r'br'
    ]

    tags = re.findall(r'</?[^>]+>', text)
    for tag in tags:
        tag_id = re.search(r'^</?([^>]+)>$', tag).group(1)
        
        if not any(map(lambda t: re.match(t, tag_id), tag_regs_to_keep)):
            text = re.sub(tag, '', text)

    return text

def add_missing_tags(text, tags):
    # closing tag with no opening tag at the beginning.
    tag = re.search(r'^[^<]*</([^>]+)>', text)
    if tag:
        text = f'<{tag.group(1)}>' + text

    # opening tag with no closing tag at the end.
    tag = re.search(r'<([^>/]+)>[^<>]*$', text)
    if tag:
        text = text + f'</{tag.group(1)}>'

    # br doesn't need closing tags
    text = re.sub(r'</br>', '', text)

    for tag in tags:
        if tags[tag] > 0 and f'<{tag}>' not in text:
            text = f'<{tag}>{text}</{tag}>'

    return text


def parse_bible(file_path, output_folder):
    os.makedirs(os.path.dirname(output_folder), exist_ok=True)
    verses = []
    chapters = []
    sub_heading = []
    # test_file = open('bible/output/text.txt', 'w')

    # previous_mode = ''

    for line in open(file_path, 'r').readlines():
        line = line.strip()

        # is_verse = line.startswith('<V>')
        # is_poetry = line.startswith('<P>')

        line = line.replace('<LE>', '') # destroy optional long E tag.
        line = line.replace('<,>', '') # destroy 'superior comma' tag.

        line = verse_ref_to_tags(line) # convert verse_ref to tags
        line = replace_tags(line) # convert strong, italic, and small caps into tags

        line = strongs_ref_to_tags(line)
        line = combine_strongs_tags(line)

        line = remove_continuing_quotes(line)

        line = re.sub(r'\^', '', line) # caret was used to mark beginning of verse earlier to make regex work. Remove it afterward.

        # if is_poetry and previous_mode == 'V':
        #     line = '<br>' + line
        
        # if is_verse:
        #     previous_mode = 'V'
        # elif is_poetry:
        #     previous_mode = 'P'

        # strongs_tag_reg = r'\w+<M[GH][^>]+?>'
        # words_with_tag_reg = r'\w*<[^\s]+>\w+?</[^\s]+>\w*'
        # words_with_format_tag = r'\w*\{[\w\s]*\}\w*'
        # word_reg = r'\w+'
        # other_tag_reg = r'<[^\s]+?>'
        # whitespace_reg = r'\s+'

        if '<verse_ref>' in line:
            vr_tag = re.search(r'<verse_ref><book>(\d+)</book><chapter>(\d+)</chapter><verse>(\d+)</verse></verse_ref>', line)
            book = int(vr_tag.group(1))
            chapter = int(vr_tag.group(2))
            verse = int(vr_tag.group(3))

            # remove verse_ref
            line = re.sub(r'<verse_ref>.*</verse_ref>', '', line)

            new_paragraph = line.startswith('<br>')
            if new_paragraph:
                # remove starting line break
                line = re.sub(r'^<br>', '', line)


            # remove unwanted tags
            line = remove_unwanted_tags(line)

            parts = re.split(r'(</?M[^>]+>)', line)

            current_strongs = None
            current_text = None
            current_tags = {
                'em': 0,
                'small': 0,
                'strong': 0,
            }

            bible_texts = []

            for part in parts:
                if is_strongs_tag(part): # strongs tag
                    strongs = get_strongs_tag(part)
                    if not current_strongs: # there is no current_strongs so this must be an opening strongs tag.
                        current_strongs = strongs
                    elif strongs != current_strongs: # strongs tag does not match current_strongs!
                        raise Exception(f'new strongs tag {strongs} does not match current strongs tag {current_strongs}. verse_ref: {book} {chapter}:{verse}')
                    else: # strongs tag does match current_strongs tag does this must be a closing tag.
                        if not current_text:
                            raise Exception(f'no current text for strongs {current_strongs}')
                        
                        bible_texts.append(BibleText(current_text, dictionary_code=current_strongs))

                        current_strongs = None
                        current_text = None
                else: # just text
                    current_text = add_missing_tags(part, current_tags)

                    for text in re.split('(</?[^>]+>)', part):
                        if is_tag(text):
                            if 'br' in text:
                                continue 

                            opening_tag, closing_tag = get_opening_tag(text), get_closing_tag(text)

                            if opening_tag:
                                current_tags[opening_tag] += 1

                            if closing_tag:
                                current_tags[closing_tag] -= 1
                                if current_tags[closing_tag] < 0:
                                    raise Exception(f"closing tag count shouldn't be negative: {closing_tag} {current_tags[closing_tag]}")

                    if not current_strongs:
                        bible_texts.append(BibleText(current_text))
                        current_text = None

            verse_obj = BibleVerse(bible_texts, new_paragraph, '<br>'.join(sub_heading), verse, book, chapter)
            verses.append(verse_obj)
            sub_heading = []

            # v = f"{get_bible_book(book)} {chapter}:{verse}\n{verse_text}"
            # output_file.write(v + '\n')
            # print(v)
        elif is_sub_head(line):
            match = re.match(r'^<S[SH]>(.+)</S[SH]>$', line)
            sub_heading.append(remove_unwanted_tags(replace_tags(match.group(1))))
            # sh = f"---{sub_heading}---\n"
            # sub_heading = replace_tags(sub_heading)
            # output_file.write(sh + '\n')
            # print(sh)

    # json.dump([chapter.to_data() for chapter in chapters], output_file, ensure_ascii=False, indent=4)

    for book in range(1, 67):
        book_verses = [verse for verse in verses if verse.book == book]
        book_name = get_bible_book(book)
        count = len(book_verses)
        chapter = 1
        chapters = []
        while count > 0: 
            chapter_verses = [verse for verse in book_verses if verse.chapter == chapter]
            if chapter_verses:
                chapters.append(BibleChapterAndVerses(book_name, chapter, chapter_verses))
            count -= len(chapter_verses)
            chapter += 1

        file_path = f'{output_folder}/{book_name}.json'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        json.dump([chapter.to_data() for chapter in chapters], open(file_path, 'w'), ensure_ascii=False, indent=4)


def write_tagged_occurrences(input_folder_path, output_folder, hebrew_dict_file_path, greek_dict_file_path):
    if not os.path.exists(input_folder_path):
        raise Exception(f"{input_folder_path} does not exist.")
    
    os.makedirs(output_folder, exist_ok=True)

    hebrew_dict = parse_dictionary(hebrew_dict_file_path)
    greek_dict = parse_dictionary(greek_dict_file_path)
    
    tagged_occurrences = {}
    
    for book in bible_books:
        file_path = f'{input_folder_path}/{book}.json'
        book_data = json.load(open(file_path))
        
        for chapter_obj in book_data:
            chapter = chapter_obj['chapter']
            for verse_obj in chapter_obj['verses']:
                verse = verse_obj['verseNumber']

                for verse_text_obj in verse_obj['texts']:
                    if 'dictionaryCode' not in verse_text_obj:
                        continue

                    dict_code = verse_text_obj['dictionaryCode']

                    text = verse_text_obj['text']

                    if dict_code not in tagged_occurrences:
                        tagged_occurrences[dict_code] = {
                            "occurrences": [],
                        }

                        l = dict_code[0]
                        num = dict_code[1:]
                        entry = None
                        if l == 'G' and num in greek_dict:
                            entry = greek_dict[num]
                        elif l == 'H' and num in hebrew_dict:
                            entry = hebrew_dict[num]

                        if entry:
                            tagged_occurrences[dict_code]['originalWord'] = entry['originalWord']
                            tagged_occurrences[dict_code]['definition'] = entry['definition']

                    tagged_occurrences[dict_code]["occurrences"].append({
                        "verseReference": [book, chapter, verse],
                        "text": text,
                        "textStems": [porterStemmer.stem(w) for w in word_tokenize(remove_all_tags(text))]
                    })
                    # print(big_dictionary[dict_code])
                    # input()
    
    for strongs in tagged_occurrences.keys():
        json.dump(tagged_occurrences[strongs], open(f'{output_folder}/{strongs}.json', 'w'), indent=4)


if __name__ == '__main__':
    # parse bible with tagged strongs numbers
    print('Parsing bible with tagged strongs numbers...', end='')
    bible_file_path = open('bible_tagged_file_path.txt', 'r').read()
    parse_bible(bible_file_path, output_folder='bible/output/bible_tagged')
    print('Done.')

    # compile occurrences keyed by strongs number
    print('Compiling occurrences keyed by strongs number...', end='')
    hebrew_dictionary_file_path, greek_dictionary_file_path = open('bible_dictionary_file_paths.txt', 'r').read().split('\n')
    write_tagged_occurrences('bible/output/bible_tagged', 'bible/output/bible_tagged_occurrences', hebrew_dictionary_file_path, greek_dictionary_file_path)
    print('Done.')