from django.core.management import setup_environ
import urllib2
import settings
setup_environ(settings)
import math
import threading, datetime

from tmv_app.models import *

class DBManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "DB Manager"
        self.tasks = []
        self.current = None
        self.end = False
        self.task_count = 0
    def add(self, task):
        self.tasks.append(task)
        print "* %s %s: added" % (datetime.datetime.now(), task.name)
    def add_start(self, task):
        self.tasks.insert(0, task)
        print "* %s %s: added (to start of queue)" % (datetime.datetime.now(), task.name)
    def cancel_task(self, task):
        self.tasks.remove(task)
        print "* %s %s: canceled" % (datetime.datetime.now(), task.name)
    def get_ident(self):
        self.task_count += 1
        return self.task_count
    def run(self):
        while not self.end or len(self.tasks) != 0:
            if len(self.tasks) != 0:
                self.current = self.tasks.pop(0)
                if self.current and not self.current.cancel:
                    try:
                        self.current.run()
                    except:
                        self.tasks.insert(0, self.current)

DB_LOCK = threading.Lock()
DBM = DBManager()
DBM.start()

def init():
    stats = RunStats(start=datetime.datetime.now(), batch_count=0, last_update=datetime.datetime.now())
    stats.save()
    
    settings = Settings(doc_topic_score_threshold=1, doc_topic_scaled_score=True)
    settings.save()

def signal_end():
    DBM.end = True

def increment_batch_count():
    DB_LOCK.acquire()
    stats = RunStats.objects.get(id=1)
    stats.batch_count += 1
    stats.last_update = datetime.datetime.now()
    stats.topic_titles_current = False
    print stats.last_update
    stats.save()
    DB_LOCK.release()

def print_task_update():
    print "** CURRENT TASKS **"
    tasks = DBM.tasks[:]
    if DBM.current:
        tasks.insert(0, DBM.current)
    for task in tasks:
        active = "active" if task == DBM.current else "waiting"
        canceled = task.cancel
        print "   %s %s\t\t%s\t\t%s" % (task.time_created, task.name, canceled, active)
    print "** END **"

class DBTask():
    def __init__(self, name):
        self.cancel = False
        self.time_created = datetime.datetime.now()
        self.ident = DBM.get_ident()
        self.name = "DB Task-%s (%s)" % (self.ident, name)
    def safe_cancel(self):
        self.cancel = True        
        print "* %s %s: canceled" % (datetime.datetime.now(), self.name)
    def run(self):
        print "* %s %s: started" % (datetime.datetime.now(), self.name)
        DB_LOCK.acquire()
        print "* %s %s: DB lock acquired" % (datetime.datetime.now(), self.name)
        self.db_write()
        DB_LOCK.release()
        print "* %s %s: DB lock released" % (datetime.datetime.now(), self.name)
        print "* %s %s: ended" % (datetime.datetime.now(), self.name)
    def db_write(self):
        pass


def add_term(title):
    term = Term(title=title)
    term.save()

class TermsTask(DBTask):
    def __init__(self, terms):
        self.terms = terms
        DBTask.__init__(self, "write all terms")
    def db_write(self):
        for t in self.terms:
            add_term(t.strip())

def add_terms(terms):
    DBM.add(TermsTask(terms))


def add_topic(title):
    topic = Topic(title=title)
    topic.save()

class TopicsTask(DBTask):
    def __init__(self, no_topics):
        self.no_topics = no_topics
        DBTask.__init__(self, "write all topics")
    def db_write(self):
        for t in range(self.no_topics):
            add_topic("Topic " + str(t+1))

def add_topics(no_topics):
    DBM.add(TopicsTask(no_topics))


def add_doc(title, content):
    DB_LOCK.acquire()
    doc = Doc(title=urllib2.unquote(title), content="")
    doc.save()
    DB_LOCK.release()
    return doc.id

def add_docs(doc_array):
    doc_ids = []
    DB_LOCK.acquire()
    for d in doc_array:
        doc = Doc(title=urllib2.unquote(d[0]), content="")
	doc.save()
        doc_ids.append(doc.id)
    DB_LOCK.release()
    return doc_ids


def add_doc_topic(doc_id, topic_id, score, scaled_score):
    if score < 1:
        return
    dt = DocTopic(doc=doc_id, topic=(topic_id+1), score=score, scaled_score=scaled_score)
    dt.save()

class DocTopicsTask(DBTask):
    def __init__(self, doc_topics):
        self.doc_topics = doc_topics
        DBTask.__init__(self, "write doc topics")
    def db_write(self):
        for dt in self.doc_topics:
            add_doc_topic(dt[0], dt[1], dt[2], dt[3])

def add_doc_topics(doc_topic_array):
    DBM.add(DocTopicsTask(doc_topic_array))


def clear_topic_terms(topic):
    try:
        TopicTerm.objects.filter(topic=(topic+1)).delete()
    except:
        return

def add_topic_term(topic, term, score):
    if score >= .005:
        tt = TopicTerm(topic=(topic+1), term=(term+1), score=score)
        tt.save()

class UpdateTopicTermsTask(DBTask):
    def __init__(self, no_topics, topic_terms):
        self.no_topics = no_topics
        self.topic_terms = topic_terms
        DBTask.__init__(self, "update topic terms")
    def db_write(self):
        for topic in range(self.no_topics):
            clear_topic_terms(topic)
        for tt in self.topic_terms:
            add_topic_term(tt[0], tt[1], tt[2])

def update_topic_terms(no_topics, topic_terms):
    for task in DBM.tasks:
        if isinstance(task, UpdateTopicTermsTask):
            task.safe_cancel()
            DBM.cancel_task(task)

    DBM.add_start(UpdateTopicTermsTask(no_topics, topic_terms))
