from books_of_the_bible import get_bible_book
from format import BibleBook, BibleChapterAndVerses, BibleVerse
import re
import os
import json

output_file_path = 'bible/output/bible'
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

def replace_tags(text):
    text = re.sub(r'<\\>', '<small>', text)
    text = re.sub(r'</>', '</small>', text)
    text = re.sub(r'{', '<i>', text)
    text = re.sub(r'}', '</i>', text)
    return text

def parse_bible(file_path, output_folder_path):
    os.makedirs(os.path.dirname(output_folder_path), exist_ok=True)
    verses = []
    chapters = []
    sub_heading = ''
    prev_chapter = 1
    prev_book = ''

    for line in open(file_path, 'r').readlines():
        parts = re.findall(r'<\$.*?\$.*?>|<.+?>|{{\d+::\d+}}\d+<T>|[^<\+]+', line)

        verse_ref = ''.join(vr for vr in parts if is_verse_ref(vr))
        verse_text = ''.join(vt for vt in parts if is_verse_text(vt))

        if verse_ref:
            match = re.match(r'^{{(\d+)::(\d+)}}(\d+)<T>$', verse_ref)
            book = int(match.group(1))
            chapter = int(match.group(2))
            verse = int(match.group(3))
            has_paragraph_break = '<PM>' in line

            verse_text = replace_tags(verse_text)

            # if prev_book == '':
            #     prev_book = book

            # if chapter != prev_chapter:
            #     chapter_obj = BibleChapterAndVerses(get_bible_book(prev_book), prev_chapter, verses)
            #     prev_chapter = chapter
            #     verses = []
            #     chapters.append(chapter_obj)

            #     if book != prev_book:
            #         prev_book = book

                # if book != prev_book:
                #     file_path = f'{output_folder_path}/{get_bible_book(prev_book)}.json'
                #     os.makedirs(os.path.dirname(file_path), exist_ok=True)
                #     json.dump([chapter.to_data() for chapter in chapters], open(file_path, 'w'), ensure_ascii=False, indent=4)

                #     prev_book = book
                #     chapters = []

            verse_obj = BibleVerse(verse_text, has_paragraph_break, sub_heading, verse, book, chapter)
            verses.append(verse_obj)
            sub_heading = ''

            v = f"{get_bible_book(book)} {chapter}:{verse}\n{verse_text}"
            # output_file.write(v + '\n')
            # print(v)
        elif is_sub_head(line):
            match = re.match(r'^<SH>(.+)</SH>$', line)
            sub_heading = match.group(1)
            sh = f"---{sub_heading}---\n"
            sub_heading = replace_tags(sub_heading)
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

        file_path = f'{output_folder_path}/{book_name}.json'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        json.dump([chapter.to_data() for chapter in chapters], open(file_path, 'w'), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    parse_bible(bible_file_path, output_file_path)