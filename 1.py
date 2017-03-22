import tokenizer
import re
T = tokenizer.TweetTokenizer()

f = open('nyusha_nyusha.txt', 'r', encoding='utf-8')
tweet = f.read()
f.close()
tokens = T.tokenize(tweet)

scanner = re.Scanner([
    (r"((https?:\/\/|www)|\w+\.(\w{2-3}))([\w\!#$&-;=\?\-\[\]~]|%[0-9a-fA-F]{2})+",    lambda scanner, token: ("URL", token)),
	(r"^\+?\d{1}?[-\(]?\d{3}[\)-]?\d{3}-?\d{2}-?\d{2}$", lambda scanner, token: ("PHONE", token)),
	(r"(?:@\w+)",    lambda scanner, token: ("USER", token)),
	(r"(?:\#\w+)", lambda scanner, token: ("HASHTAG", token)),
	(r"[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]",    lambda scanner, token: ("EMAILS", token)),
	(r"<[^>\s]+>", lambda scanner, token: ("HTML-TAGS", token)),
	(r"[\-]+>|<[\-]+",    lambda scanner, token: ("ASCII_ARROWS", token)),
	(r"#(?=\w+)", lambda scanner, token: ("HASH", token)),
	(r"^(RT)", lambda scanner, token: ("RETWIT", token)),
	(r"[😎|😘|☺|😍|☺|️️|❤|☝|🏻|🏻|🙈|🙌|😘|✨|😍|😋|😳|😌|🐾|✈|💋|😽|☀|💪|👉|🎬|😂|😇|✊|☕|😜|😇|😍|😘|😂|😎|😬|🔥|😍|😀]", lambda scanner, token: ("EMOJI", token)),
	(r"(?:[<>]?[:;=8][\-o\*\']?[\)\]\(\[dDpP*/\:\}\{@\|\\]|[\)\]\(\[dDpPсСрР3/\:\}\{@\|\\][\-o\*\']?[:;=8][<>]?)", lambda scanner, token: ("SMILE", token)),
	(r'[!|$|%|&|"|,|.|;|:|-|?|*|«|»|\(|\)|-]+', lambda scanner, token: ("PUNCT", token)),
	(r"(?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_])|(?:[+\-]?\d+[,/.:-]\d+[+\-]?)|(?:[\w_]+)|(?:\.(?:\s*\.){1,})|(?:\S)",lambda scanner, token: ("WORD", token))
	], re.UNICODE)


f2 = open('output.txt', 'w', encoding='utf-8')
for i in range(len(tokens)):
	results, remainder = scanner.scan(tokens[i])
	for j in results:
		f2.write(str(i) + '\t' + j[0] + '\t' + j[1] + '\r\n')
f2.close()

