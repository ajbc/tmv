from django.db import models

class Topic(models.Model):
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.title)

class Term(models.Model):    
    title = models.CharField(max_length=50)

class TopicTerm(models.Model):
    topic = models.IntegerField()
    term = models.IntegerField()
    score = models.FloatField()

class Doc(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    
    def word_count(self):
        return len(str(self.content).split())

class DocTopic(models.Model):
    doc = models.IntegerField()
    topic = models.IntegerField()
    score = models.FloatField()
    scaled_score = models.FloatField()

class DocTerm(models.Model):
    doc = models.IntegerField()
    term = models.IntegerField()
    score = models.FloatField()

class RunStats(models.Model):
    start = models.DateTimeField()
    batch_count = models.IntegerField()
    last_update = models.DateTimeField()
    topic_titles_current = models.BooleanField()

class Settings(models.Model):
    doc_topic_score_threshold = models.FloatField()
    doc_topic_scaled_score = models.BooleanField()
