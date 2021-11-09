import random
from datetime import datetime


def format_quote(list_quotes, number):
    if number <= 0:
        index = random.randint(0, len(list_quotes)-1)
    else:
        index = number-1
    try:
        selected_quote = list_quotes[index]
    except IndexError:
        return 'There\'s not that many quotes available!'
    return '{}: <{}/{}> {}'.format(selected_quote[0], index+1, len(list_quotes), selected_quote[1])


def parse_quote_request(msg, conn):
    command = str(msg.clean_content)[len('/quote '):]
    serv_id = str(msg.guild.id)
    chan_id = str(msg.channel.id)
    cursor = conn.cursor()
    try:
        number = int(command)
        cursor.execute('''
                SELECT author, text FROM Quotes
                WHERE serv_id = %s
                ORDER BY date''', (serv_id,))
        list_quotes = []
        for i in cursor:
            list_quotes.append(i)
        if len(list_quotes) < 1:
            return 'No quotes found for this server.'
        return format_quote(list_quotes, number)
    except ValueError:
        pass
    except TypeError:
        pass
    if len(command) < 1:
        cursor.execute('''
        SELECT author, text FROM Quotes
        WHERE serv_id = %s
        ORDER BY date''', (serv_id,))
        list_quotes = []
        for i in cursor:
            list_quotes.append(i)
        if len(list_quotes) < 1:
            return 'No quotes found for this server.'
        return format_quote(list_quotes, 0)
    elif command.startswith('add'):
        trash, author, content = command.split(' ', 2)
        cursor.execute('''
        INSERT INTO Quotes(id, serv_id, chan_id, author, text, date)
        VALUES(DEFAULT, %s, %s, %s, %s, %s)
        ''', (serv_id, chan_id, author, content, str(datetime.today().date())))
        conn.commit()
        return 'Quote added!'
    else:
        try:
            author, number = command.rsplit(' ', 1)
        except:
            author = command
            number = 0
        cursor.execute('''
        SELECT author, text FROM Quotes
        WHERE serv_id = %s
        AND LOWER(author) = LOWER(%s)
        ORDER BY date''', (serv_id, author))
        list_quotes = []
        for i in cursor:
            list_quotes.append(i)
        if len(list_quotes) < 1:
            return 'No quotes found for ' + author
        return format_quote(list_quotes, int(number))
