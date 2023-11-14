from books_of_the_bible import get_bible_book
import re
import os

output_file_path = 'bible/output/bible.txt'
bible_file_path = open('file_path.txt', 'r').read()

def is_long_tag(text):
    return re.match(r'^<\$.*?\$.*?>$', text) != None

def is_tag(text):
    return re.match(r'^<.+?>$', text) != None

def is_verse_ref(text):
    return re.match(r'^{{\d+::\d+}}\d+<T>$', text) != None

def is_verse_text(text):
    return re.match(r'^[^<>]+$', text) != None

def is_sub_head(text):
    return re.match(r'^<SH>.+</SH>$', text) != None

def parse_bible(file_path, output_file_path):
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, 'w') as output_file:
        for line in open(file_path, 'r').readlines():
            parts = re.findall(r'<\$.*?\$.*?>|<.+?>|{{\d+::\d+}}\d+<T>|[^<\+]+', line)

            verse_ref = ''.join(vr for vr in parts if is_verse_ref(vr))
            verse_text = ''.join(vt for vt in parts if is_verse_text(vt))

            if verse_ref:
                match = re.match(r'^{{(\d+)::(\d+)}}(\d+)<T>$', verse_ref)
                book = int(match.group(1))
                chapter = int(match.group(2))
                verse = int(match.group(3))

                v = f"{get_bible_book(book)} {chapter}:{verse}\n{verse_text}"
                output_file.write(v + '\n')
                print(v)
            elif is_sub_head(line):
                match = re.match(r'^<SH>(.+)</SH>$', line)
                sub_heading = match.group(1)
                sh = f"---{sub_heading}---\n"
                output_file.write(sh + '\n')
                print(sh)



if __name__ == '__main__':
    parse_bible(bible_file_path, output_file_path)
        