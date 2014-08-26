# filter.py

import znc
import re

class filter(znc.Module):
    description = "Filter out messages that match a particular channel/regex"
    quickstore = dict()         # Used to hold compiled REs

    def OnLoad(self, args, message):
        '''Startup

        Iterate through self.nv, copying the key and the compiled RE into
        self.quickstore.  Also register new commands.
        '''
        for key in self.nv.keys():
            self.quickstore[key] = re.compile(self.nv[key])
        return True
        
    def OnChanMsg(self, nick, channel, message):
        '''Message handler

        When a message comes in, check it against the filter list to see if
        it should be passed on to the client or just dropped on the floor.
        '''
        c = str(channel.GetName())
        if c in self.quickstore:
            if self.quickstore[c].match(str(message)): return znc.HALT # Match: drop it!
        if nick in self.quickstore:
            if self.quickstore[nick].match(str(message)): return znc.HALT # Match: drop it!
        if nick+c in self.quickstore:
            if self.quickstore[nick+c].match(str(message)): return znc.HALT # Match: drop it!
        return znc.CONTINUE     # Nah, let the user see the message.

    def addfilter(self, key, value):
        '''Private function to handle adding filters'''
        self.nv[key] = value
        self.quickstore[key] = re.compile(value)
        return

    def delfilter(self, key):
        '''Private function to handle removing filters'''
        try: del self.nv[key]
        except: pass
        try: del self.quickstore[key]
        except: pass
        return


    # Web UI
    
    def GetWebMenuTitle(self):
        '''Title of the web menu item '''
        return "Filter"

    def OnWebRequest(self, websock, pagename, tmpl):
        '''Web UI handler.

        Everything comes through here.  Fortunately, we only have one web
        page and two functions, so it's pretty easy.
        '''
        if str(pagename) == 'index': # Just draw the index page
            for key,value in self.nv.items(): # Add all the items to the page
                if not '#' in key:
                    channel = ''
                    nick = key
                else:
                    parts = key.split('#', 1)
                    nick = parts[0]
                    channel = '#' + parts[1]
                row = tmpl.AddRow("FilterLoop")
                row['nick'] = nick
                row['channel'] = channel
                row['regex'] = value
            return True
        elif str(pagename) == 'addfilter': # Add a new filter
            # This try/except is here to protect us from stupid user tricks.
            try:
                nick = websock.GetParam('nick') or ''
                channel = websock.GetParam('channel') or ''
                myregex = websock.GetParam('regex')
                print("nick is '%s'" % nick)
                print("channel is '%s'" % channel)
                print("myregex is '%s'" % myregex)
                self.addfilter(nick+channel, websock.GetParam('regex'))
            except Exception as e:
                print(e)
                pass
            websock.Redirect(self.GetWebPath()) # The only displayable page is the index.
            return True
        elif str(pagename) == 'delfilter': # Drop an old filter
            nick = websock.GetParam('nick', False) or ''
            channel = websock.GetParam('channel', False) or ''
            self.delfilter(nick+channel)
            websock.Redirect(self.GetWebPath()) # The only displayable page is the index.
            return True
        return False # This will make the ZNC web server through a "page doesn't respond" error.

    

