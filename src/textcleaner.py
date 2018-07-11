# -*- coding: utf-8 -*-
"""
TextCleaner with regex
Francesco Pareo e Matteo Sartori - Bologna
"""

import re
    
class text_cleaner(object):

    def __init__(self, rm_punct = False, rm_tabs = False, rm_newline = False, rm_digits = False,
                   tolower = False, rm_hashtags = False, rm_tags = False, rm_urls = False, rm_email=False,
                   rm_html_tags = False, rm_apostrophe = False, rm_underscore = False, rm_minus = False):
        self.rm_punct = rm_punct
        self.rm_tabs = rm_tabs
        self.rm_newline = rm_newline
        self.rm_digits = rm_digits
        self.rm_html_tags = rm_html_tags
        self.tolower = tolower
        self.rm_hashtags = rm_hashtags 
        self.rm_tags = rm_tags
        self.rm_urls = rm_urls
        self.rm_email = rm_email
        self.rm_apostrophe = rm_apostrophe
        self.rm_minus = rm_minus
        self.rm_underscore = rm_underscore
        self.pattern_list = list()
        self.repl_list = list()

        # compile the regex
        self.regex_compiler()
    
    
    def regex_compiler(self):

        if self.rm_urls:  
            self.pattern_list.append( re.compile( r'\b((?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?)\b' ) )
            self.repl_list.append( ' ' )
            self.pattern_list.append( re.compile( r'www\S+' ) )
            self.repl_list.append( ' ' )
        if self.rm_email:
            self.pattern_list.append(re.compile(r'\b([\w.-]+?@\w+?\.\w+?)\b' ) )
            self.repl_list.append( ' ' )
        if self.rm_html_tags:
            self.pattern_list.append( re.compile( r'(&#?[A-z0-9]{1,8};)' ) )
            self.repl_list.append( ' ' )
        if self.rm_hashtags:
            self.pattern_list.append( re.compile( r'#+[A-z0-9\_]+' ) )
            self.repl_list.append( ' ' )
        if self.rm_tags:
            self.pattern_list.append( re.compile( r'@+[A-z0-9\_]+((:)?)' ) )
            self.repl_list.append( ' ' )
        if self.rm_tabs:
            self.pattern_list.append( re.compile( r'\t' ) )
            self.repl_list.append( ' ' )
            self.pattern_list.append( re.compile( r'\v' ) )
            self.repl_list.append( ' ' )
        if self.rm_newline:
            self.pattern_list.append( re.compile( r'\n' ) )
            self.repl_list.append( ' ' )
        if self.rm_punct:
            self.pattern_list.append( re.compile( ur'[[\]\\]|[^0-9A-z\u00E0\u00E1\u00E8\u00E9\u00EC\u00ED\s\u00F2\u00F3\u00F9\u00FA]' ) )
            self.repl_list.append( ' ' )
        else:
            self.pattern_list.append( re.compile( ur"[[\]\\]|[^0-9A-z\u00E0\u00E1\u00E8\u00E9\u00EC\u00ED\s\u00F2\u00F3\u00F9\u00FA!;?.,:\'\-]" ) )
            self.repl_list.append( ' ' )
            self.pattern_list.append( re.compile( r"([!?,.:;'])([!?,.:;']*)" ) )
            self.repl_list.append( r'\1 ' )
        if self.rm_apostrophe:
            self.pattern_list.append( re.compile( r"\'" ) )
            self.repl_list.append( ' ' )
        if self.rm_underscore:
            self.pattern_list.append( re.compile( r"\_" ) )
            self.repl_list.append( ' ' )
        if self.rm_minus:
            self.pattern_list.append( re.compile( r"\-" ) )
            self.repl_list.append( ' ' )
        if self.rm_digits: 
            self.pattern_list.append( re.compile( r'[0-9]' ) )
            self.repl_list.append( ' ' )

            
        #remove start space
        self.pattern_list.append( re.compile( r"^\s+" ) )
        self.repl_list.append( r'' )
        #remove end space  
        self.pattern_list.append( re.compile( r"\s+\Z" ) ) # analogo a r'[ ]+$'
        self.repl_list.append( r'' )
        #remove useless spaces
        self.pattern_list.append( re.compile( r"[ ]+" ) )
        self.repl_list.append( r' ' )
        

    def regex_applier(self, text):
        for i in range(0, len( self.pattern_list )):
            text = self.pattern_list[i].sub( string=text, repl=self.repl_list[i])  
        if self.tolower:
            text = text.lower()
        return text


