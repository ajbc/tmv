from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context, RequestContext
from tmv_app.models import *
from django.db.models import Q
from django.shortcuts import *
from django.forms import ModelForm
import random, sys, datetime
import urllib2

# the following line will need to be updated to launch the browser on a web server
TEMPLATE_DIR = sys.path[0] + '/templates/'

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

def topic_detail(request, topic_id):    
    update_topic_titles()
    response = ''
    
    template_file = open(TEMPLATE_DIR + 'topic.html', 'r')
    topic_template = Template(template_file.read())
    
    topic = Topic.objects.get(id=topic_id)
    topicterms = TopicTerm.objects.filter(topic=topic_id).order_by('-score')
    doctopics = DocTopic.objects.filter(topic=topic_id).order_by('-score')[:50]
    
    terms = []
    term_bar = []
    remainder = 1
    remainder_titles = ''
    
    for tt in topicterms:
        term = Term.objects.get(pk=tt.term)
        
        terms.append(term)
        if tt.score >= .01:
            term_bar.append((True, term, tt.score * 100))
            remainder -= tt.score
        else:
            if remainder_titles == '':
                remainder_titles += term.title
            else:
                remainder_titles += ', ' + term.title
    term_bar.append((False, remainder_titles, remainder*100))
    
    topics = []
    
    docs = []
    for dt in doctopics:
        docs.append(Doc.objects.get(pk=dt.doc))
    
    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()
    
    topic_page_context = Context({'nav_bar': nav_bar, 'topic': topic, 'terms': terms, 'term_bar': term_bar, 'docs': docs})
    
    return HttpResponse(topic_template.render(topic_page_context))

def term_detail(request, term_id):
    update_topic_titles()
    response = ''
    
    template_file = open(TEMPLATE_DIR + 'term.html', 'r')
    term_template = Template(template_file.read())
    
    term = Term.objects.get(id=term_id)
    
    topics = {}
    for topic in Topic.objects.all():
        tt = TopicTerm.objects.filter(topic=topic.id, term=term_id)
        if len(tt) > 0:
            topics[topic] = tt[0].score
    
    sorted_topics = sorted(topics.keys(), key=lambda x: -topics[x])
    topic_tuples = []
    if len(topics.keys()) > 0:
        max_score = max(topics.values())
        for topic in sorted_topics:
            topic_tuples.append((topic, topics[topic], topics[topic]/max_score*100))
    
    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()

    term_page_context = Context({'nav_bar': nav_bar, 'term': term, 'topic_tuples': topic_tuples})
    
    return HttpResponse(term_template.render(term_page_context))

def doc_detail(request, doc_id):
    update_topic_titles()
    response = ''
    print "doc: " + str(doc_id)
    template_file = open(TEMPLATE_DIR + 'doc.html', 'r')
    doc_template = Template(template_file.read())
    
    doc = Doc.objects.get(id=doc_id)
    doctopics = DocTopic.objects.filter(doc=doc_id).order_by('-score')

    topics = []
    pie_array = []
    dt_threshold = Settings.objects.get(id=1).doc_topic_score_threshold
    print dt_threshold
    dt_thresh_scaled = Settings.objects.get(id=1).doc_topic_scaled_score
    for dt in doctopics:
        if ((not dt_thresh_scaled and dt.score >= dt_threshold) or (dt_thresh_scaled and dt.scaled_score*100 >= dt_threshold)):
            topic = Topic.objects.get(pk=dt.topic)
            topics.append(topic)
            print topic.title
            if not dt_thresh_scaled:
                pie_array.append([dt.score, '/topic/' + str(topic.id), 'topic_' + str(topic.id)])
            else:
                pie_array.append([dt.scaled_score, '/topic/' + str(topic.id), 'topic_' + str(topic.id)])
        else:
            print (dt.score, dt.scaled_score)
   
    if doc.content == '':
        doc.content = get_doc_display(doc)
        doc.save()
     
    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()
    
    doc_page_context = Context({'nav_bar': nav_bar, 'doc': doc, 'topics': topics, 'pie_array': pie_array})
    
    return HttpResponse(doc_template.render(doc_page_context))

def topic_list_detail(request):
    update_topic_titles()
    response = ''
    
    template_file = open(TEMPLATE_DIR + 'topic_list.html', 'r')
    list_template = Template(template_file.read())
    
    topics = Topic.objects.all()

    terms = []
    for t in topics:
        topicterms = TopicTerm.objects.filter(topic=t.id).order_by('-score')[:5]
        temp =[]
        term_count = 5
        for tt in topicterms:
            temp.append(Term.objects.get(pk=tt.term))
            term_count -= 1
        for i in range(term_count):        
            temp.append(None)
        terms.append(temp)
    
    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()

    div_topics = []
    div_terms = []
    rows = []
    n = 3
    for i in xrange(0, len(topics), n):
        temp = [] 
        for j in range(5):
            K = min(len(topics), i+n)
            t = [terms[k][j] for k in range(i,K,1)]
            while len(t) < n:
                t.append(None)
            temp.append(t)
        tops = topics[i:i+n]
        while len(tops) < n:
            tops.append(None)
        rows.append((tops, temp))

    list_page_context = Context({'nav_bar': nav_bar, 'rows': rows})
    
    return HttpResponse(list_template.render(list_page_context))

def topic_presence_detail(request):
    update_topic_titles()
    response = ''
    
    template_file = open(TEMPLATE_DIR + 'topic_presence.html', 'r')
    presence_template = Template(template_file.read())
    
    topics = {}
    for topic in Topic.objects.all():
        score = sum([dt.score for dt in DocTopic.objects.filter(topic=topic.id)])
        topics[topic] = score
    
    sorted_topics = sorted(topics.keys(), key=lambda x: -topics[x])
    topic_tuples = []
    max_score = max(topics.values())
    for topic in sorted_topics:
        topic_tuples.append((topic, topics[topic], topics[topic]/max_score*100))
    
    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()

    presence_page_context = Context({'nav_bar': nav_bar, 'topic_tuples': topic_tuples})
    
    return HttpResponse(presence_template.render(presence_page_context))


def stats(request):
    template_file = open(TEMPLATE_DIR + 'stats.html', 'r')
    stats_template = Template(template_file.read())

    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()

    stats_page_context = Context({'nav_bar': nav_bar, 'num_docs': Doc.objects.count(), 'num_topics': Topic.objects.count(), 'num_terms': Term.objects.count(), 'start_time': RunStats.objects.get(id=1).start, 'elapsed_time': (datetime.datetime.now() - RunStats.objects.get(id=1).start), 'num_batches': RunStats.objects.get(id=1).batch_count, 'last_update': RunStats.objects.get(id=1).last_update})

    return HttpResponse(stats_template.render(stats_page_context))

class SettingsForm(ModelForm):
    class Meta:
        model = Settings

def settings(request):
    template_file = open(TEMPLATE_DIR + 'settings.html', 'r')
    settings_template = Template(template_file.read())
   
    nav_bar = open(TEMPLATE_DIR + 'nav_bar.html', 'r').read()
   
    settings_page_context = Context({'nav_bar': nav_bar, 'settings': Settings.objects.get(id=1)})

    #return HttpResponse(settings_template.render(settings_page_context))
    return render_to_response('settings.html', settings_page_context, context_instance=RequestContext(request))

def apply_settings(request):
    settings = Settings.objects.get(id=1)
    print settings.doc_topic_score_threshold
    print settings.doc_topic_scaled_score
    form = SettingsForm(request.POST, instance=settings)
    print form
    print settings
    #TODO: add in checks for threshold (make sure it's a float)
    settings.doc_topic_score_threshold = float(request.POST['threshold'])
   
    print settings.doc_topic_score_threshold
    print settings.doc_topic_scaled_score
    settings.save()

    return HttpResponseRedirect('/topic_list')

def update_topic_titles():
    stats = RunStats.objects.get(id=1)
    if not stats.topic_titles_current:
        for topic in Topic.objects.all():
            topicterms = TopicTerm.objects.filter(topic=topic.id).order_by('-score')[:3]
            if topicterms.count() < 3:
                continue
            new_topic_title = '{' + Term.objects.get(pk=topicterms[0].term).title + ', ' + Term.objects.get(pk=topicterms[1].term).title + ', ' + Term.objects.get(pk=topicterms[2].term).title + '}'
            topic.title = new_topic_title
            topic.save()
        stats.topic_titles_current = True
        stats.save()

def topic_random(request):
    return HttpResponseRedirect('/topic/' + str(random.randint(1, Topic.objects.count())))

def doc_random(request):
    return HttpResponseRedirect('/doc/' + str(random.randint(1, Doc.objects.count())))

def term_random(request):
    return HttpResponseRedirect('/term/' + str(random.randint(1, Term.objects.count())))

def get_doc_display(doc):
    url = "http://en.wikipedia.org/wiki/" + doc.title
    url2 = "http://en.wikipedia.org/wiki/" + doc.title.replace(" ", "_").replace("&amp;", '&')
    
    f = ''
    try:
        f = opener.open(url.encode('utf-8'))
    except urllib2.HTTPError:
        try:
            f = opener.open(url2)
        except:
            return "This page could not be found."
    site = f.read()
    
    # get past the unwanted content at the start of the html file
    end_cur = site.find('</h1>')

    start_cur = site[end_cur:].find('<table class="vertical-navbox nowraplinks"')
    while (start_cur != -1):
        while (start_cur != -1):
            new_end_cur = end_cur + start_cur + site[end_cur + start_cur:].find('</table>')
            start_cur = site[end_cur + start_cur + len('<table') : new_end_cur].find('<table')
            end_cur = new_end_cur
        start_cur = site[end_cur:].find('<table class="vertical-navbox nowraplinks"')

    # cherrypick desired content, up to a certain length
    new_start_cur = site[end_cur:].find('<p')
    new_end_cur = site[end_cur:].find('</p>')

    pair_key = 0
    pairs = [('<p', '</p>'), ('<span class="mw-headline"', '</span>'), ('<div id="toctitle">', '</div>'), ('<ul>','</ul>')]

    content = ''
    while (new_start_cur != -1 and new_end_cur != -1 and len(content) < 5000):
        content_addition = site[end_cur+new_start_cur:end_cur+new_end_cur+len(pairs[pair_key][1])]
        if pair_key == 1:
            content += '\n<h3>' + content_addition + '</h3>'
        else:
            content += '\n' + content_addition

        end_cur = end_cur + new_end_cur + len(pairs[pair_key][1])
        
        new_start_cur = -1
        new_end_cur = -1
        for pair in pairs:
            start_cur = site[end_cur:].find(pair[0])
            if start_cur != -1 and (new_start_cur == -1 or start_cur < new_start_cur):
                new_start_cur = start_cur
                new_end_cur = site[end_cur:].find(pair[1])
                temp_start_cur = new_start_cur
                count = 0
                while count <10 and site[end_cur + temp_start_cur + len(pair[0]) : end_cur + new_end_cur].find(pair[0]) != -1:
                    temp_start_cur = temp_start_cur + site[end_cur + temp_start_cur + len(pair[0]):].find(pair[0]) + len(pair[0])
                    new_end_cur = new_end_cur + site[end_cur + new_end_cur + len(pair[1]):].find(pair[1])  + len(pair[1])
                    count += 1
                pair_key = pairs.index(pair)
    
    # make sure links connect to wikipedia.org properly
    content = unicode(content, errors='ignore')
    content = content.replace('href="/wiki', 'href="http://www.wikipedia.org/wiki')
    content = content.replace(u'href="#', 'href="' + url + '#')
    content = content.replace("\n\n", "</p>\n\n<p>")
    
    return content
