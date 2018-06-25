from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.
class Conference(models.Model):
	name = models.CharField(max_length=2048)
	description = models.TextField(blank=True)
	code = models.CharField(max_length=16)
	link = models.URLField(blank=True)
	start_date = models.DateField(default='2018-01-01')
	end_date = models.DateField(default='2018-01-01')
	def __str__(self):
		return self.name
	
class EventType(models.Model):
	event_type = models.CharField(max_length=256)
	conference = models.ForeignKey(Conference,on_delete=models.CASCADE, null=True)
	def __str__(self):
		return self.event_type + ' (' + self.conference.name + ')'

class Location(models.Model):
	location = models.CharField(max_length=1024)
	conference = models.ForeignKey(Conference,on_delete=models.CASCADE, null=True)
	def __str__(self):
		return self.location + ' (' + self.conference.name + ')'

class Village(models.Model):
	village = models.CharField(max_length=1024)
	conference = models.ForeignKey(Conference,on_delete=models.CASCADE, null=True)
	def __str__(self):
		return self.village + ' (' + self.conference.name + ')'

class Vendor(models.Model):
	title = models.CharField(max_length=1024)
	description = models.TextField(blank=True)
	link = models.URLField(max_length=2048,blank=True)
	partner = models.BooleanField(default=False)
	conference = models.ForeignKey(Conference,on_delete=models.CASCADE, null=True)
	def __str__(self):
		return self.title + ' (' + self.conference.name + ')'

class Speaker(models.Model):
	sptitle = models.CharField(max_length=2048,blank=True)
	group = models.ForeignKey(Group,on_delete=models.CASCADE,null=True)
	who = models.CharField(max_length=2048)
	twitter = models.CharField(max_length=512,blank=True)
	link = models.URLField(blank=True)
	bio = models.TextField(blank=True)
	conference = models.ForeignKey(Conference,on_delete=models.CASCADE, null=True)
	def __str__(self):
		return self.who + ' (' + self.conference.name + ')'

class Event(models.Model):
	event_id = models.CharField(max_length=32)
	group = models.ForeignKey(Group,on_delete=models.CASCADE,null=True)
	title = models.CharField(max_length=2048)
	description = models.TextField(blank=True)
	link = models.URLField(blank=True)
	location = models.ForeignKey(Location,on_delete=models.CASCADE, null=True)
	event_type = models.ForeignKey(EventType,on_delete=models.CASCADE, null=True)
	conference = models.ForeignKey(Conference,on_delete=models.CASCADE, null=True)
	speakers = models.ManyToManyField(Speaker)
	exploit = models.BooleanField(default=False)
	tool = models.BooleanField(default=False)
	demo = models.BooleanField(default=False)
	includes = models.CharField(max_length=256,blank=True)
	dctv_channel = models.CharField(max_length=32,blank=True)
	start_date = models.DateTimeField(default='2018-01-01T00:00:00-00:00')
	end_date = models.DateTimeField(default='2018-01-01T01:00:00-00:00')
	def __str__(self):
		return self.title + ' (' + self.conference.name + ')'
	
