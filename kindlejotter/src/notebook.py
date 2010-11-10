#import cgi
import os
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template


def doRender(handler,tname='page.html', values={}):
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
#Display Form

class MainPage(webapp.RequestHandler):
    def get(self):
        doRender(self, 'page.html')
        
    def post(self):
        #note = Note()
        
        content = self.request.get('content')
             
        subject = self.request.get('subject')
        
        if content == '' or subject == '' :
            doRender(
                     self, 'page.html',
                     {'error' : 'Please fill in all fields for note to be saved'})
            return
        
        newnote = Note(content=content, subject=subject);
                       
        newnote.put()
         
        self.redirect('/')

#Display Form
class notebook(webapp.RequestHandler):
    def get(self):
                            
        notest = db.Query(Note)
        notelist = notest.fetch(limit=100)
        doRender(self, 'readnote.html',
                 {'notelist': notelist, })
        
class filternotes(webapp.RequestHandler):
    def get(self):
                            
        notest = db.Query(Note)
        notelist = notest.fetch(limit=5)
        doRender(self, 'readnote.html',
                 {'notelist': notelist, })
        

        

class show (webapp.RequestHandler):
    def get(self):
            qs = self.request.query_string
            qstr = str(qs)
   
            que = db.GqlQuery("SELECT * FROM Note WHERE ANCESTOR IS :1", qstr)
                                      
            results = que.fetch(limit=10)

            doRender(self, 'shownote.html',
                 {'results': results,'qs': qstr,})   

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

            doRender(self, 'edit.html',
                 {'results': results,}) 
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
                                        ('/', MainPage),
                                        ('/getnote', notebook),
                                        ('/filter', filternotes),
                                        ('/show', show),
                                        ('/edit', edit),
                                        ('/delete', delete),
                                    ],
                                     debug=True)
wsgiref.handlers.CGIHandler().run(application)