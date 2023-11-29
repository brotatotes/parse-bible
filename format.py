import json

# export interface BibleVerse {
#   text: string;
#   parapraphBreak?: boolean;
#   subtitle?: string;
# }

# export interface BibleChapterAndVerses {
#   book: string;
#   chapter: number;
#   verses: { [verseNumber: number]: BibleVerse };
# }

class BibleVerse:
    def __init__(self, text, paragraph_break, subtitle, verse_number, book, chapter):
        self.text = text
        self.paragraph_break = paragraph_break
        self.subtitle = subtitle
        self.verse_number = verse_number
        self.book = book
        self.chapter = chapter

    def to_data(self):
        data = {
            "text": self.text,
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
