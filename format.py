import json

# this class is for storing portions of bible text including hebrew + greek info.
# multiple BibleText can make up a BibleVerse
class BibleText:
    def __init__(self, text, dictionary_code=None, italic=False, bold=False, smallcaps=False):
        self.text = text
        self.dictionary_code = dictionary_code
        self.italic = italic
        self.bold = bold
        self.smallcaps = smallcaps

    def to_data(self):
        data = {
            "text": self.text,
        }

        if self.dictionary_code:
            data["dictionaryCode"] = self.dictionary_code

        if self.italic:
            data["italic"] = self.italic

        if self.bold:
            data["bold"] = self.bold

        if self.smallcaps:
            data["smallcaps"] = self.smallcaps

        return data


class BibleVerse:
    def __init__(self, bible_texts, paragraph_break, subtitle, verse_number, book, chapter):
        self.bible_texts = bible_texts
        self.paragraph_break = paragraph_break
        self.subtitle = subtitle
        self.verse_number = verse_number
        self.book = book
        self.chapter = chapter

    def to_data(self):
        data = {
            "texts": [t.to_data() for t in self.bible_texts],
            "paragraphBreak": self.paragraph_break,
            "subtitle": self.subtitle,
            "verseNumber": self.verse_number
        }

        return data
    
class BibleChapterAndVerses:
    def __init__(self, book, chapter, verses):
        self.book = book
        self.chapter = chapter
        self.verses = verses

    def to_data(self):
        data = {
            "book": self.book,
            "chapter": self.chapter,
            "verses": [verse.to_data() for verse in self.verses]
        }

        return data
    
class BibleBook:
    def __init__(self, book, chapters):
        self.book = book
        self.chapters = chapters

    def to_data(self):
        data = {
            "book": self.book,
            "chapters": [chapter.to_data() for chapter in self.chapters]
        }

        return json.dumps(data)
    
class Bible:
    def __init__(self, books):
        self.books = books

    def to_data(self):
        data = {
            "books": [book.to_data() for book in self.books]
        }

        return data
