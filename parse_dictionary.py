import re
import json

def translate_tags(text):
    text = text.replace('<IT>', '<i>').replace('</IT>', '</i>')
    text = text.replace('<B>', '<b>').replace('</B>', '</b>')
    text = re.sub(r'<[/]*O>', '', text)
    text = re.sub(r'<[/]*UNI>', '', text)
    text = re.sub(r'<[/]*TRAU_WORD>', '', text)
    text = re.sub(r'<GREEK>.*</GREEK>', '', text)
    return text

def write_dictionaries(hebrew_dictionary_file_path, greek_dicitonary_file_path, output_file_path):
    hebrew_data = parse_dictionary(hebrew_dictionary_file_path)
    greek_data = parse_dictionary(greek_dicitonary_file_path)

    data = {
        'Hebrew': hebrew_data,
        'Greek': greek_data
    }

    json.dump(data, open(output_file_path, 'w'), indent=4)


def parse_dictionary(dictionary_file_path):
    dictionary_raw_text = open(dictionary_file_path).read()

    dictionary_data = {}

    # reg = re.compile(r'^@STR\d = <B[I]*>(.+?)\.</B[I]*>$.*?^@ECU_word = (.+?)$.*?^@TRA = (.+?)$', re.MULTILINE | re.DOTALL)
    reg_group = re.compile(r'^@STR\d(?:(?!@STR).)*', re.MULTILINE | re.DOTALL)
    for group in reg_group.findall(dictionary_raw_text):
        reg_tag = re.compile(r'^@(.+?) = (.+?)$', re.MULTILINE)

        num = ''
        ecu = []
        tra = []

        for tag, content in reg_tag.findall(group):
            if tag.startswith('STR'):
                num = re.search(r'<B[I]*>(.+?)\.</B[I]*>', content).group(1)
            elif re.match(r'ECU\d*_word', tag) != None:
                ecu.append(content)
            elif tag.startswith('TRA'):
                tra.append(translate_tags(content))

        dictionary_data[num] = {
            'originalWord': ecu,
            'definition': tra
        }

    return dictionary_data

    # for num, ecu, tra in reg.findall(dictionary_raw_text):
    #     tra = translate_tags(tra)

    #     dictionary_data[num] = {
    #         'originalWord': ecu,
    #         'definition': tra
    #     }

    # return dictionary_data


if __name__ == '__main__':
    output_file_path = 'bible/output/bible_dictionary.json'
    hebrew_dictionary_file_path, greek_dicitonary_file_path = open('bible_dictionary_file_paths.txt', 'r').read().split('\n')

    write_dictionaries(hebrew_dictionary_file_path, greek_dicitonary_file_path, output_file_path)

