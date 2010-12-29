#import cgi
import os
import wsgiref.handlers
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template


def doRender(handler,tname='welcome.html', values={}):
    temp = os.path.join(
        os.path.dirname(__file__),
        'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    
    newval = dict(values)
    newval['path'] = handler.request.path
    
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True
             
#Database properties of what a 'Note' is
class Note (db.Model):
    content=db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    subject=db.StringProperty(multiline=True)
    user = db.UserProperty()
    userid = db.StringProperty()
    sharewith = db.StringProperty()
#Display Form

class welcome(webapp.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            
            greeting = ("Signed in as: %s (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
            
            doRender(self, 'page.html', {'greeting' : greeting,})
            
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/"))

        #self.response.out.write("<html><body>%s</body></html>" % greeting)
            
            
            doRender(self, 'welcome.html', {'greeting' : greeting,})


class MainPage(webapp.RequestHandler):
    def get(self):
        
        user = users.get_current_user()      
        greeting = ("Signed in as: %s (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        
        doRender(self, 'page.html',{'greeting':greeting, })
        
    def post(self):
        #note = Note()
        user = users.get_current_user()
        userid = user.user_id()
        
        content = self.request.get('content')
             
        subject = self.request.get('subject')
        
        #sharewith = self.request.get ('sharewith')
        
        if "@" in content:
            firstsplit = content.partition("@")[2]
            secondsplit = firstsplit.split(" ")[0]
            sharewith = secondsplit
        
        if content == '' or subject == '' :
            doRender(
                     self, 'page.html',
                     {'error' : 'Please fill in all fields for note to be saved'})
            return
        
        newnote = Note(content=content, subject=subject, user=user,  userid = userid, sharewith = sharewith,);
                       
        newnote.put()
         
        self.redirect('/entry')

#Display Form
class notebook(webapp.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        userid = user.user_id()
        nick_name = user.nickname()
                            
        #notest = db.Query(Note)
        notest = db.GqlQuery ("SELECT * FROM Note WHERE userid = :1 ", userid)
        sharedquery = db.GqlQuery ("SELECT * FROM Note WHERE sharewith = :1", nick_name)
        
        
        notelist = notest.fetch(limit=100)
        sharedlist = sharedquery.fetch(limit=100)
        
        greeting = ("Signed in as: %s (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        
        doRender(self, 'readnote.html',
                 {'notelist': notelist,'sharedlist' : sharedlist, 'greeting':greeting, })
        
class filternotes(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        userid = user.user_id()                    
        notest = db.GqlQuery ("SELECT * FROM Note WHERE userid = :1", userid)
        notelist = notest.fetch(limit=5)
        
        user = users.get_current_user()      
        greeting = ("Signed in as: %s (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        
        doRender(self, 'readnote.html',
                 {'notelist': notelist,'greeting':greeting, })
        

        

class show (webapp.RequestHandler):
    def get(self):
            qs = self.request.query_string
            qstr = str(qs)
   
            que = db.GqlQuery("SELECT * FROM Note WHERE ANCESTOR IS :1", qstr)
                                      
            results = que.fetch(limit=1)
            
                
            user = users.get_current_user()      
            greeting = ("Signed in as: %s (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
            for note in results:
                if note.user == user:
                    deleteflag =1
                    doRender(self, 'shownote.html',
                    {'results': results,'qs': qstr,'greeting':greeting,'deleteflag':deleteflag})   
                else:
                    doRender(self, 'shownote.html',
                    {'results': results,'qs': qstr,'greeting':greeting})
                    
class delete (webapp.RequestHandler):
    def get(self):
            qs = self.request.query_string
            qstr = str(qs)
   
            que = db.GqlQuery("SELECT * FROM Note WHERE ANCESTOR IS :1", qstr)
                                      
            results = que.fetch(limit=1)
            for result in results:
                result.delete()
            
            self.redirect('/getnote') 

class edit (webapp.RequestHandler):
    def get(self):
            
            qs = self.request.query_string
            qstr = str(qs)
 
            que = db.GqlQuery("SELECT * FROM Note WHERE ANCESTOR IS :1", qstr)
                         
            results = que.fetch(limit=1)
            
            user = users.get_current_user()      
            greeting = ("Signed in as: %s (<a href=\"%s\">Sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
            
            doRender(self, 'edit.html',
                 {'results': results,'greeting':greeting,}) 
    def post(self):
        
        qs = self.request.query_string
        qstr = str(qs)
        
        editnote = db.GqlQuery("SELECT * FROM Note WHERE ANCESTOR IS :1", qstr)
        results = editnote.fetch(limit=1)
        
        content = self.request.get('content')          
        subject = self.request.get('subject')

        if content == '' or subject == '' :
            doRender(
                     self, 'edit.html',
                     {'results' : results, 'error' : 'Please fill in all fields for note to be saved.'})
            return
        
        editnote = db.GqlQuery("SELECT * FROM Note WHERE ANCESTOR IS :1", qstr).get()
        
        editnote.content = content
        editnote.subject = subject                      
        editnote.put()
         
        self.redirect('/getnote')
                    
application = webapp.WSGIApplication(
                                     [
                                        ('/', welcome),
                                        ('/entry', MainPage),
                                        ('/getnote', notebook),
                                        ('/filter', filternotes),
                                        ('/show', show),
                                        ('/edit', edit),
                                        ('/delete', delete),
                                    ],
                                     debug=True)
wsgiref.handlers.CGIHandler().run(application)