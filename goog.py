import requests
import sys
from html.parser import HTMLParser
import argparse

'''
Parsing google results has a couple of states to be in:
  1) looking for main
  2) looking for 'g' 
  3) building 'g' response
  4) outputing 'g' summary
  5) discarding other results


states:
lm (looking for main)
m (in main, finding groups)
g (building group)

'''
class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state = 'lm'
        self.res = []
        self.ind = 0
        self.mctr = 0
        self.gctr = 0
        self.text = ''
        self.title = ''
        self.link = ''
        self.body = None
    
    def handle_starttag(self, tag, attrs):     
        self.body = None
        if self.state == 'm':
            if tag == 'div' and ('class', 'ZINbbc xpd O9g5cc uUPGi') in attrs:
                self.state = 'g'
                self.gctr = 1
                self.res.append({})
                self.text = ''
                self.title = ''
                self.link = ''
            elif tag == 'div':
                self.mctr += 1

        elif self.state == 'g':
            if tag == 'div' and ('class','BNeawe vvjwJb AP7Wnd') in attrs:
                self.body = 'title'
            if tag == 'div' and ('class','BNeawe UPmit AP7Wnd') in attrs:
                self.body = 'link'
            if tag == 'div' and ('class','BNeawe s3v9rd AP7Wnd') in attrs:
                self.body = 'body'

            if tag =='div':
                self.gctr += 1                
        else:
            if tag == 'div' and ('id', 'main') in attrs:
                self.state = 'm'
                self.mctr = 1
        
    def handle_endtag(self,tag):
        # if wer're in main, uncount divs until we reach 0, then we're out of main
        if self.state == 'm':
            if tag == 'div':
                self.mctr -= 1
            if self.mctr == 0:
                self.state = 'lm'
            pass

        # if we're in a group, uncount divs until we reach 0, then we're out of group
        elif self.state == 'g':
            if tag == 'div':
                self.gctr -= 1
            if self.gctr == 0:
                self.res[self.ind]['title'] = self.title
                self.res[self.ind]['text'] = self.text
                self.res[self.ind]['link'] = self.link
                self.state = 'm'
                self.ind += 1
            pass
        
        else:
            pass
        
    def handle_data(self, data):
        if self.body == 'title':
            self.title = data
        elif self.body == 'body':
            self.text += data
        elif self.body == 'link':
            self.link = data
        else:
            pass

def hit_goog(query):
    r = requests.get('https://www.google.com/search',params={'q':query})
    parser = Parser()
    if r.status_code == 200:
        parser.feed(r.text)
        return (parser.res)
    return "Failed"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Returns the first page of google results from the commandline.")
    parser.add_argument("text", nargs = '*')
    parsed = parser.parse_args()

    if parsed.text != None and len(parsed.text) > 0:
        data = " ".join(parsed.text)
    else:
        data = input()
        
    res = hit_goog(data)
    for r in res:
        if len(r["title"])== 0 or len(r["link"]) == 0:
            continue
        print("-"*20)
        print(r["title"])
        print(r["text"])
        print(r["link"])
        print("-"*20)
    
