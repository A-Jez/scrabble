from psycopg2 import connect, Error
from string import punctuation
from re import match
from sys import argv


def create_regex(letters):
    wildcard = letters.count('_')
    letters_reg = ''.join(letters)
    if wildcard == 0:
        return f'^[{letters_reg}]+$'
    else:
        return f'^[{letters_reg}]+$'

def sanitize_input(input):
    return ''.join(c for c in input if c not in punctuation).upper()

def initdb():
    client = connect(
        database='quotes',
        host='localhost',
        user='spider',
        password='pass123'
    )
    return client.cursor()

def get_words(pattern):
    db = initdb()
    db.execute("SELECT word, value from words WHERE word ~ %s ORDER BY value desc;", (pattern, ))
    return db.fetchmany(3)



if len(argv) < 2:
    raise ValueError('[SCRABBLE] - NO ARGUMENTS PROVIDED: prog PHRASE')

if not match('^[A-Za-z_]*$', argv[1]):
    raise ValueError('[SCRABBLE] - INVALID INPUT - MUST MATCH [A-Za-z_]+')



input_string = sanitize_input(argv[1])
input_array = list(input_string)

regex = create_regex(input_array)

print(regex)

result = get_words(regex)

print('RESULTS: ')
for i, val in enumerate(result):
    word, value = val
    print(f'\t #{i} - {word} with {value} points!')
