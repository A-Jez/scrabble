# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from string import punctuation
from psycopg2 import connect, Error

VALUE_MAP = {
    'A': 1, 'E': 1, 'I': 1, 'N': 1, 'O': 1, 'R': 1, 'S': 1, 'W': 1, 'Z': 1,
    'C': 2, 'D': 2, 'K': 2, 'L': 2, 'M': 2, 'P': 2, 'T': 2, 'Y': 2,
    'B': 3, 'G': 3, 'H': 3, 'J': 3, 'Ł': 3, 'U': 3,
    'Ą': 5, 'Ę': 5, 'F': 5, 'Ó': 5, 'Ś': 5, 'Ż': 5,
    'Ć': 6,
    'Ń': 7,
    'Ź': 9,
    '_': 0
}

class QuotesPipeline(object):
    def process_item(self, item, spider):
        processed_quote = self.extract_words(item['quote'])
        
        result = {}
        for words in processed_quote:
            word, value = self.get_word_value(words)
            result[word] = value
        return result

    def get_word_value(self, word):
        value = 0
        for letter in word:
            value += VALUE_MAP.get(letter, 0)
        
        return (word, value)

    def extract_words(self, quote):
        return ''.join(c for c in quote if c not in punctuation).upper().split()


class PostgresPipeline(object):
    def __init__(self, db_name, db_host, db_port, db_user, db_passwd):
        self.db_name = db_name
        self.db_user = db_user
        self.db_host = db_host
        self.db_port = db_port
        self.db_passwd = db_passwd
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_name=crawler.settings.get('DB_NAME', 'postgres'),
            db_user=crawler.settings.get('DB_USER', 'postgres'),
            db_host=crawler.settings.get('DB_HOST', 'localhost'),
            db_port=crawler.settings.get('DB_PORT', 5432),
            db_passwd=crawler.settings.get('DB_PASSWD', '')
        )    
    def open_spider(self, spider):
        try:
            self.client = connect(
                database=self.db_name,
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_passwd
            )
            self.db = self.client.cursor()
        except Error as err:
            print(err)
    
    def close_spider(self, spider):
        self.db.close()
        self.client.close()
    
    def process_item(self, item, spider):
        for key, value in item.items():
            self.db.execute("""
                INSERT INTO words(word, value)
                    SELECT %s, %s
                WHERE NOT EXISTS (
                SELECT 1 FROM words WHERE word=%s
            )""", (key, value, key))

        try:
            self.client.commit()
        except Error as err:
            print(f'Error while processing {item}: {err}')
        return item