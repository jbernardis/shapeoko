from threading import Thread

def iswhite(c):
    return c == " " or c == "\n" or c == "\r" or c == "\t"

class Scanner(Thread):
    def __init__(self, q, fn):
        self.q = q
        self.fp = open(fn, "r")
        self.lex = Thread(target=self.rthread)
        self.lex.start()
        
    def rthread(self):
        inword = False
        incomment = False
        word = ""
        for ln in self.fp:
            hasDash = False
            hasDecimal = False
            for c in ln:
                if incomment:
                    pass
                
                elif inword:
                    if c.isdigit():
                        word += c
                    elif c == '-' and not hasDash:
                        word += c
                        hasDash = True
                    elif c == '.' and not hasDecimal:
                        word += c
                        hasDecimal = True
                    else:
                        self.q.put(word)
                        inword = False
                        hasDash = False
                        hasDecimal = False
                        word = ""
                        if c.isalpha():
                            inword = True
                            word = c
                        elif c in ['#', ';', '(']:
                            incomment = True
                        elif iswhite(c):
                            pass
                        else:
                            print("unknown character1: ", c)
                else:
                    if c.isalpha():
                        word = c.upper()
                        inword = True
                    elif c in ['#', ';', '(']:
                        incomment = True
                        
                    elif iswhite(c):
                        pass
                    else:
                        print("unknown character2: ", c)
                        
            incomment = False
                        
            
        self.fp.close()
        self.q.put(None)

