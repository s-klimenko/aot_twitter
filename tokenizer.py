#tokenizer, borrowing/built heavily from nltk
import nltk
from nltk.tokenize.casual import remove_handles, reduce_lengthening, _str_to_unicode, _replace_html_entities # EMOTICONS, EMOTICON_RE
import re
import reg
import unicodedata

#urls - nltk version
URLS = r"""         # Capture 1: entire matched URL
  (?:
  https?:               # URL protocol and colon
    (?:
      /{1,3}                # 1-3 slashes
      |                 #   or
      [a-z0-9%]             # Single letter or digit or '%'
                                       # (Trying not to match e.g. "URI::Escape")
    )
    |                   #   or
                                       # looks like domain name followed by a slash:
    [a-z0-9.\-]+[.]
    (?:[a-z]{2,13})
    /
  )
  (?:                   # One or more:
    [^\s()<>{}\[\]]+            # Run of non-space, non-()<>{}[]
    |                   #   or
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\) # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)             # balanced parens, non-recursive: (...)
  )+
  (?:                   # End with:
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\) # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)             # balanced parens, non-recursive: (...)
    |                   #   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]  # not a space or one of these punct chars
  )
  |                 # OR, the following to match naked domains:
  (?:
    (?<!@)                  # not preceded by a @, avoid matching foo@_gmail.com_
    [a-z0-9]+
    (?:[.\-][a-z0-9]+)*
    [.]
    (?:[a-z]{2,13})
    \b
    /?
    (?!@)                   # not succeeded by a @,
                            # avoid matching "foo.na" in "foo.na@example.com"
  )
"""



#my emoticons, borrowed & expanded from https://github.com/g-c-k/idiml/blob/master/predict/src/main/resources/data/emoticons.txt

# Twitter specific:
HASHTAG = r"""(?:\#\w+)"""
TWITTER_USER = r"""(?:@\w+)"""
EMOTICONS = r"""
   (?:
     [<>]?
     [:;=8]                     # eyes
     [\-o\*\']?                 # optional nose
     [\)\]\(\[dDpP*/\:\}\{@\|\\] # mouth
     |
     [\)\]\(\[dDpPсСрР/\:\}\{@\|\\] # mouth
     [\-o\*\']?                 # optional nose
     [:;=8]                     # eyes
     [<>]?
   )"""
#separately compiled regexps
TWITTER_USER_RE = re.compile(TWITTER_USER, re.UNICODE)
HASHTAG_RE = re.compile(HASHTAG, re.UNICODE)
HASH_RE = re.compile(r'#(?=\w+)', re.UNICODE)
#my url version, nltk's doesn't work for separate regexp
URL_RE = re.compile(r"""((https?:\/\/|www)|\w+\.(\w{2-3}))([\w\!#$&-;=\?\-\[\]~]|%[0-9a-fA-F]{2})+""", re.UNICODE)

# more regular expressions for word compilation, borrowed from nltk
#phone numbers
PHONE = r"""(?:(?:\+?[01][\-\s.]*)?(?:[\(]?\d{3}[\-\s.\)]*)?\d{3}[\-\s.]*\d{4})"""

# email addresses
EMAILS = r"""[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]"""
# HTML tags:
HTML_TAGS = r"""<[^>\s]+>"""
# ASCII Arrows
ASCII_ARROWS = r"""[\-]+>|<[\-]+"""
#long non-word, non-numeric repeats
#HANGS = r"""([^a-zA-Z0-9])\1{3,}"""
# Remaining word types:
WORDS = r"""
    (?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_]) # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots.
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
TWITTER_REGEXPS = [EMOTICONS, URLS, PHONE, HTML_TAGS, ASCII_ARROWS, TWITTER_USER, HASHTAG, EMAILS, WORDS]

# regexps for regularization: for now, hard-coded
# TODO: probabilistic way of recognizing contractions without ',
# determining what T word is actually intended, etc.
CONTRACTIONS_NEG = re.compile(r"cannot\b|\w+n't\b|shant|wont", re.I) #add cant? technically a separate word
CONTRACTIONS_FUT = re.compile(r"\b(i'll|he'll|she'll|you'll|youll|we'll)\b", re.I) #ill, hell, shell, well
# assuming "'d" is modal "should/would" for now; "had" also possible but not coded here
CONTRACTIONS_MOD = re.compile(r"\b(i'd|you'd|youd|he'd|she'd|we'd)\b", re.I) #id, hed, shed, wed
CONTRACTIONS_COPULA = re.compile(r"\b(i'm|im|you're|youre|we're|they're|theyre|he's|hes|shes|she's|it's)\b", re.I) #were, its
CONTRACTIONS_HAVE = re.compile(r"\w+'ve\b", re.I)
GOTTA = re.compile(r'\bgotta\b', re.I)
GONNA = re.compile(r'\bgonna\b', re.I)
HAFTA = re.compile(r'\bhafta\b', re.I)
WANNA = re.compile(r'\bwanna\b', re.I)

class TweetTokenizer():

    def __init__(self, preserve_case=True, preserve_handles=True, preserve_hashes=True, regularize=False, preserve_len=True, preserve_emoji=True, preserve_url=True):
        ''' Tweet tokenizer with options:
        ::param preserve_case:: if False, reduces text to lower case. Default True,
        leaves case intact.
        ::type preserve_case:: bool
        ::param preserve_handles:: if False, strips Twitter user handles from text. Default True,
        leaves user handles intact.
        ::type preserve_handles:: bool
        ::param preserve_hashes:: if False, strips the hash symbol from hashtags (but
        does not delete the hashtag word). Default True, leaves hashtags intact.
        ::type preserve_hashes:: bool
        ::param regularize:: if True, regularizes the text for common English contractions,
        resulting in two word sequences like "can" "not" instead of single token "can't".
        Default False, does not regularize.
        ::type regularize:: bool
        ::param preserve_len:: if False, reduces three or more sequences of the same character
        down to only three repetitions. Default True, does not reduce lengthening.
        ::type preserve_len:: bool
        ::param preserve_emoji:: if False, strips emoji from the text. Default True,
        leaves emoji intact.
        ::type preserve_emoji:: bool
        ::param preserve_url:: if False, strips url addresses from the text. Default True,
        leaves urls intact.
        type preserve_url:: bool
        '''
        self.preserve_case = preserve_case
        self.preserve_handles = preserve_handles
        self.preserve_hashes = preserve_hashes
        self.regularize = regularize
        #self.R = reg.Regularizer()

        self.preserve_len = preserve_len
        self.preserve_emoji = preserve_emoji
        self.preserve_url = preserve_url
        self.WORD_RE = re.compile(r"""(%s)""" % "|".join(TWITTER_REGEXPS), re.VERBOSE | re.I | re.UNICODE)

    def strip_emoji(self, text):
        '''Take out emoji. Returns doc string.
        ::param text:: tweet
        ::type doc:: str
        '''
        text = ''.join(c for c in text if unicodedata.category(c) != 'So') # almost works perfectly
        return text

    def tokenize(self, text):
        '''Casual speech tokenizer wrapper function, closely based on nltk's version.
        Returns a list of words.
        ::param text:: tweet text
        ::type text:: str
        '''
        text = _replace_html_entities(text)
        if not self.preserve_handles:
            text = re.sub(TWITTER_USER_RE, ' ', text)
        if not self.preserve_hashes:
            text = re.sub(HASH_RE, '', text)
        if not self.preserve_url:
            text = re.sub(URL_RE, ' ', text)
        if not self.preserve_len:
            text = reduce_lengthening(text)
        if self.regularize:
            text = self.R.regularize(text)
        if not self.preserve_emoji:
            text = self.strip_emoji(text)
        words = self.WORD_RE.findall(text)
        if not self.preserve_case:
            words = list(map((lambda x : x if EMOTICON_RE.search(x) else
                              x.lower()), words))
        return words





