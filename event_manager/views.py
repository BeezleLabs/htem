#
# HackerTracker Event Manager
#
# created_by: @sethlaw

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.db.models import Q

import json
import re
import datetime

from .models import Event, Location, EventType, Speaker, Vendor, Village, Conference, Article, FAQ, Notification

def get_user_conference(request):
	for group in request.user.groups.all():
		if Conference.objects.filter(code=group.name):
			return Conference.objects.get(code=group.name)
		else:
			return None

def get_user_village(request):
	c = None
	v = None
	for group in request.user.groups.all():
		m = re.search('^(\w+):(.*)$',group)
		if m:
			c = Conference.objects.get(code=m.group(0))
			v = Village.objects.get(village=m.group(1))
	return c,v

# UI
def index(request):
    if request.user.is_authenticated:
        return redirect("/event_manager/events/")
    else:
        return redirect("/event_manager/login/")

@login_required
def dashboard(request):
	return render(
		request,
		'event_manager/dashboard.html'
	)

@login_required
def search(request):
	q = request.GET.get('q')
	event_list = None
	speakers = None
	if request.session["code"] is not None and q is not None:
		con = Conference.objects.get(code=request.session["code"])
		event_list = list(Event.objects.filter( Q(conference=con),
									   Q(title__icontains=q) | Q(description__icontains=q)
									   ))
		speakers = list(Speaker.objects.filter( Q(conference=con),
											   Q(who__icontains=q) | Q(bio__icontains=q)
											   ))

	return render(
		request,
		'event_manager/search.html',
		{
			'q': q,
			'event_list': event_list,
			'speakers': speakers
		}
	)

@login_required
def conferences(request):
	if request.user.is_superuser:
		conferences = list(Conference.objects.all().order_by('-start_date') )
		return render(
			request,
			'event_manager/conferences.html',
			{ 'conferences': conferences }
		)
	else:
		return redirect('events')

@login_required
def conference_delete(request,code=None):
	if not request.user.is_superuser:
		messages.warn(request,"Unauthorized")
	elif code is not None:
		if Conference.objects.filter(code=code):
			item = Conference.objects.get(code=code)
			item.delete()
			messages.info(request, "Conference Deleted")
		else:
			messages.warning(request, "No conference to delete")
	else:
		messages.warning(request, "No conference found")
	return conferences(request)

@login_required
def select_con(request,code=None):
	if request.user.is_superuser:
		if code != None:
			try:
				con = Conference.objects.get(code=code)
				request.session["code"] = code
				return redirect('events')
			except Conference.DoesNotExist:
				messages.warning(request,"Could not select conference " + code)
				return redirect('select_con')
		else:
			conferences = list(Conference.objects.all().order_by('-start_date'))
			return render(
				request,
				'event_manager/select_con.html',
				{ 'conferences': conferences }
			)
	else:
		return redirect('events')

@login_required
def conference(request,code=None):
	if request.user.is_superuser:
		if code is not None:
			con = Conference.objects.get(code=code)
		else:
			con = None

		if request.method == 'POST':
			if con is None:
				newcode = request.POST.get('code')
				if Conference.objects.filter(code=newcode):
					messages.warning(request,"Conference Code already exists")
					return render(request,'event_manager/conference.html')
				else:
					con = Conference.objects.create()
					messages.info(request,"Conference Created")
					grp = Group.objects.create(name=newcode)
					for m in [Event, Speaker, Location, EventType, Vendor, Village]:
						ct = ContentType.objects.get_for_model(model=m)
						perms = Permission.objects.filter(content_type=ct)
						for p in perms:
							grp.permissions.add(p)
			else:
				messages.info(request, "Conference Updated")

			con.name = request.POST.get('name',False)
			con.code = request.POST.get('code',False)
			con.description = request.POST.get('description',False)
			con.link = request.POST.get('link',False)
			con.timezone = request.POST.get('timezone',False)
			con.start_date = request.POST.get('start_date',False)
			con.end_date = request.POST.get('end_date',False)
			con.save()

			return redirect('/event_manager/conference/' + con.code + '/')

		return render(
			request,
			'event_manager/conference.html',
			{ 'conference': con }
		)
	else:
		return redirect('events')

@login_required
def events(request,code=None):
	event_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		event_list = list(Event.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		event_list = list(Event.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Event.objects.filter(conference=c):
				event_list.append(e)
	page_size = 20 if request.GET.get('page_size') is None else request.GET.get('page_size')
	page = 1 if request.GET.get('page') is None else request.GET.get('page')
	paginator = Paginator(event_list,page_size)
	paged_events = paginator.get_page(page)
	return render(
		request,
		'event_manager/events.html',
		{ 'event_list': paged_events, 'page_size': page_size }
	)

@login_required
def event_delete(request,e_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warning(request,"Unauthorized")
	elif e_id is not None:
		if Event.objects.filter(id=e_id):
			item = Event.objects.get(id=e_id)
			item.delete()
			messages.info(request, "Event Deleted")
		else:
			messages.warning(request, "No event to delete")
	else:
		messages.warning(request, "No event found")
	return events(request)

@login_required
def event(request,e_id=None):
	if e_id is not None:
		e = Event.objects.get(id=e_id)
		conference = e.conference
		et_list = list(EventType.objects.filter(conference=conference))
		sp_list = list(Speaker.objects.filter(conference=conference))
		loc_list = list(Location.objects.filter(conference=conference))
	else:
		e = None
		if request.user.is_superuser:
			et_list = EventType.objects.all()
			sp_list = Speaker.objects.all()
			loc_list = Location.objects.all()
		else:
			conference = get_user_conference(request)
			et_list = list(EventType.objects.filter(conference=conference))
			sp_list = list(Speaker.objects.filter(conference=conference))
			loc_list = list(Location.objects.filter(conference=conference))

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if e is None:
			e = Event.objects.create()
			messages.info(request, "Event Created")
		else:
			messages.info(request, "Event Updated")
		e.title = request.POST.get('title',False)
		e.description = request.POST.get('description',False)
		e.includes = request.POST.get('includes',False)
		e.link = request.POST.get('link',False)
		e.start_date = request.POST.get('start_date',False)
		e.end_date = request.POST.get('end_date',False)
		e.dctv_channel = request.POST.get('dctv_channel',False)
		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			e.conference = con
		elif e.conference is None:
			e.conference = get_user_conference(request)
		et = EventType.objects.get(id=request.POST.get('event_type',False))
		e.event_type = et
		s_loc = Location.objects.get(id=request.POST.get('location',False))
		e.location = s_loc
		s_speakers = request.POST.getlist('speakers',False)
		for r_sp in e.speakers.all():
			if r_sp.id not in s_speakers:
				e.speakers.remove(r_sp)
		if s_speakers is not False:
			for s_sp in s_speakers:
				sp = Speaker.objects.get(id=s_sp)
				e.speakers.add(sp)

		e.event_id = request.POST.get('event_id',False)
		if e.event_id is '':
			e.event_id = e.conference.code + '-' + str(e.id)
		e.save()

		return redirect('/event_manager/event/' + str(e.id) + '/')

	return render(
		request,
		'event_manager/event.html',
		{
			'e': e,
			'et_list': et_list,
			'sp_list': sp_list,
			'loc_list': loc_list,
			'cons': cons
		}
	)

# Event Types
@login_required
def event_types(request,code=None):
	if request.user.is_superuser or request.user.is_staff:
		et_list = []
		if request.session["code"] is not None:
			con = Conference.objects.get(code=request.session["code"])
			et_list = list(EventType.objects.filter(conference=con))
		elif request.user.is_superuser:
			con = None
			et_list = list(EventType.objects.all())
		else:
			for grp in request.user.groups.all():
				c = Conference.objects.get(code=grp.name)
				for e in EventType.objects.filter(conference=c):
					et_list.append(e)

		return render(
			request,
			'event_manager/event_types.html',
			{ 'types': et_list }
		)
	else:
		return redirect('events')

@login_required
def event_type_delete(request,et_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif et_id is not None:
		if EventType.objects.filter(id=et_id):
			item = EventType.objects.get(id=et_id)
			item.delete()
			messages.info(request, "Event Type Deleted")
		else:
			messages.warning(request, "No event type to delete")
	else:
		messages.warning(request, "No event type found")
	return event_types(request)

@login_required
def event_type(request,et_id=None):
	if et_id is not None:
		et_type = EventType.objects.get(id=et_id)
		conference = et_type.conference
	else:
		et_type = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if et_type is None:
			et_type = EventType.objects.create()
			messages.info(request, "Event Type Created")
		else:
			messages.info(request, "Event Type Updated")
		et_type.event_type = request.POST.get('event_type',False)
		et_type.color = request.POST.get('color',False)
		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			et_type.conference = con
		elif et_type.conference is None:
			et_type.conference = get_user_conference(request)
		et_type.save()

		return redirect('/event_manager/event_type/' + str(et_type.id) + '/')

	return render(
		request,
		'event_manager/event_type.html',
		{ 'type': et_type, 'cons': cons }
	)

# Locations
@login_required
def locations(request,code=None):
	loc_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		loc_list = list(Location.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		loc_list = list(Location.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Location.objects.filter(conference=c):
				loc_list.append(e)

	return render(
		request,
		'event_manager/locations.html',
		{ 'locations': loc_list }
	)

@login_required
def location_delete(request,loc_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif loc_id is not None:
		if Location.objects.filter(id=loc_id):
			item = Location.objects.get(id=loc_id)
			item.delete()
			messages.info(request, "Location Deleted")
		else:
			messages.warning(request, "No location to delete")
	else:
		messages.warning(request, "No location found")
	return locations(request)

@login_required
def location(request,loc_id=None):
	if loc_id is not None:
		loc = Location.objects.get(id=loc_id)
		conference = loc.conference
	else:
		loc = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if loc is None:
			loc = Location.objects.create()
			messages.info(request, "Location Created")
		else:
			messages.info(request, "Location Updated")
		loc.location = request.POST.get('location',False)
		loc.hotel = request.POST.get('hotel',False)
		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			loc.conference = con
		elif loc.conference is None:
			loc.conference = get_user_conference(request)

		loc.save()

		return redirect('/event_manager/location/' + str(loc.id) + '/')

	return render(
		request,
		'event_manager/location.html',
		{ 'loc': loc, 'cons': cons }
	)

# Speakers
@login_required
def speakers(request,code=None):
	sp_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		sp_list = list(Speaker.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		sp_list = list(Speaker.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Speaker.objects.filter(conference=c):
				sp_list.append(e)

	page_size = 20 if request.GET.get('page_size') is None else request.GET.get('page_size')
	page = 1 if request.GET.get('page') is None else request.GET.get('page')
	paginator = Paginator(sp_list,page_size)
	paged_speakers = paginator.get_page(page)	

	return render(
		request,
		'event_manager/speakers.html',
		{ 'speakers': paged_speakers, 'page_size': page_size }
	)

@login_required
def speaker_delete(request,sp_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif sp_id is not None:
		if Speaker.objects.filter(id=sp_id):
			sp = Speaker.objects.get(id=sp_id)
			sp.delete()
			messages.info(request, "Speaker Deleted")
		else:
			messages.warning(request, "No speaker to delete")
	else:
		messages.warning(request, "No speaker found")
	return speakers(request)

@login_required
def speaker(request,sp_id=None):
	if sp_id is not None:
		sp = Speaker.objects.get(id=sp_id)
		conference = sp.conference
	else:
		sp = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if sp is None:
			sp = Speaker.objects.create()
			messages.info(request, "Speaker Created")
		else:
			messages.info(request, "Speaker Updated")
		sp.sptitle = request.POST.get('sptitle',False)
		sp.who = request.POST.get('who',False)
		sp.twitter = request.POST.get('twitter',False)
		sp.link = request.POST.get('link',False)
		sp.bio = request.POST.get('bio',False)
		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			sp.conference = con
		elif sp.conference is None:
			sp.conference = get_user_conference(request)
		sp.save()

		return redirect('/event_manager/speaker/' + str(sp.id) + '/')

	return render(
		request,
		'event_manager/speaker.html',
		{ 'sp': sp, 'cons': cons }
	)

# Vendors
@login_required
def vendors(request,code=None):
	v_list = []
	if request.session["code"]  is not None:
		con = Conference.objects.get(code=request.session["code"] )
		v_list = list(Vendor.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		v_list = list(Vendor.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Vendor.objects.filter(conference=c):
				v_list.append(e)

	return render(
		request,
		'event_manager/vendors.html',
		{ 'vendors': v_list }
	)

@login_required
def vendor_delete(request,v_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif v_id is not None:
		if Vendor.objects.filter(id=v_id):
			ven = Vendor.objects.get(id=v_id)
			ven.delete()
			messages.info(request, "Vendor Deleted")
		else:
			messages.warning(request, "No vendor to delete")
	else:
		messages.warning(request, "No vendor found")
	return vendors(request)

@login_required
def vendor(request,v_id=None):
	if v_id is not None:
		ven = Vendor.objects.get(id=v_id)
		conference = ven.conference
	else:
		ven = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if ven is None:
			ven = Vendor.objects.create()
			messages.info(request, "Vendor Created")
		else:
			messages.info(request, "Vendor Updated")
		ven.title = request.POST.get('title',False)
		ven.description = request.POST.get('description',False)
		ven.link = request.POST.get('link',False)
		par = request.POST.get('partner', False)
		if par == False:
			ven.partner = False
		else:
			ven.partner = True

		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			ven.conference = con
		elif ven.conference is None:
			ven.conference = get_user_conference(request)
		ven.save()

		return redirect('/event_manager/vendor/' + str(ven.id) + '/')

	return render(
		request,
		'event_manager/vendor.html',
		{ 'vendor': ven, 'cons': cons }
	)

# News Articles
@login_required
def articles(request,code=None):
	a_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		a_list = list(Article.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		a_list = list(Article.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Article.objects.filter(conference=c):
				a_list.append(e)

	return render(
		request,
		'event_manager/articles.html',
		{ 'articles': a_list }
	)

@login_required
def article_delete(request,a_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif a_id is not None:
		if Article.objects.filter(id=a_id):
			a = Article.objects.get(id=a_id)
			a.delete()
			messages.info(request, "Article Deleted")
		else:
			messages.warning(request, "No article to delete")
	else:
		messages.warning(request, "No article found")
	return articles(request)

@login_required
def article(request,a_id=None):
	if a_id is not None:
		a = Article.objects.get(id=a_id)
		conference = a.conference
	else:
		a = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if a is None:
			a = Article.objects.create()
			messages.info(request, "Article Created")
		else:
			messages.info(request, "Article Updated")
		a.name = request.POST.get('name',False)
		a.text = request.POST.get('text',False)

		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			a.conference = con
		elif a.conference is None:
			a.conference = get_user_conference(request)
		a.save()

		return redirect('/event_manager/article/' + str(a.id) + '/')

	return render(
		request,
		'event_manager/article.html',
		{ 'article': a, 'cons': cons }
	)

# FAQ Items
@login_required
def faqs(request,code=None):
	a_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		a_list = list(FAQ.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		a_list = list(FAQ.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in FAQ.objects.filter(conference=c):
				a_list.append(e)

	return render(
		request,
		'event_manager/faqs.html',
		{ 'faqs': a_list }
	)

@login_required
def faq_delete(request,f_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif f_id is not None:
		if FAQ.objects.filter(id=f_id):
			a = FAQ.objects.get(id=f_id)
			a.delete()
			messages.info(request, "FAQ Item Deleted")
		else:
			messages.warning(request, "No FAQ item to delete")
	else:
		messages.warning(request, "No FAQ item found")
	return faqs(request)

@login_required
def faq(request,f_id=None):
	if f_id is not None:
		f = FAQ.objects.get(id=f_id)
		conference = f.conference
	else:
		f = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if f is None:
			f = FAQ.objects.create()
			messages.info(request, "FAQ Item Created")
		else:
			messages.info(request, "FAQ Item Updated")
		f.question = request.POST.get('q',False)
		f.answer = request.POST.get('a',False)

		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			f.conference = con
		elif f.conference is None:
			f.conference = get_user_conference(request)
		f.save()

		return redirect('/event_manager/faq/' + str(f.id) + '/')

	return render(
		request,
		'event_manager/faq.html',
		{ 'faq': f, 'cons': cons }
	)

# Notifications
@login_required
def notifications(request,code=None):
	a_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		a_list = list(Notification.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		a_list = list(Notification.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Notification.objects.filter(conference=c):
				a_list.append(e)

	return render(
		request,
		'event_manager/notifications.html',
		{ 'notifications': a_list }
	)

@login_required
def notification_delete(request,n_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif n_id is not None:
		if Notification.objects.filter(id=n_id):
			a = Notification.objects.get(id=n_id)
			a.delete()
			messages.info(request, "Notification Deleted")
		else:
			messages.warning(request, "No notification to delete")
	else:
		messages.warning(request, "No notification found")
	return notifications(request)

@login_required
def notification(request,n_id=None):
	if n_id is not None:
		n = Notification.objects.get(id=n_id)
		conference = n.conference
	else:
		n = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if n is None:
			n = Notification.objects.create()
			messages.info(request, "Notification Created")
		else:
			messages.info(request, "Notification Updated")
		n.text = request.POST.get('text',False)
		n.time = request.POST.get('time',False)

		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			n.conference = con
		elif n.conference is None:
			n.conference = get_user_conference(request)
		n.save()

		return redirect('/event_manager/notification/' + str(n.id) + '/')

	return render(
		request,
		'event_manager/notification.html',
		{ 'n': n, 'cons': cons }
	)

# Villages
@login_required
def villages(request,code=None):
	vil_list = []
	if request.session["code"] is not None:
		con = Conference.objects.get(code=request.session["code"])
		vil_list = list(Village.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		vil_list = list(Village.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Village.objects.filter(conference=c):
				vil_list.append(e)

	return render(
		request,
		'event_manager/villages.html',
		{ 'villages': vil_list }
	)

@login_required
def village_delete(request,vil_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
	elif vil_id is not None:
		if Village.objects.filter(id=vil_id):
			vil = Village.objects.get(id=vil_id)
			vil.delete()
			messages.info(request, "Village Deleted")
		else:
			messages.warning(request, "No village to delete")
	else:
		messages.warning(request, "No village found")
	return villages(request)

@login_required
def village(request,vil_id=None):
	if vil_id is not None:
		vil = Village.objects.get(id=vil_id)
		conference = vil.conference
	else:
		vil = None

	cons = []
	if request.user.is_superuser:
		cons = Conference.objects.all()

	if request.method == 'POST':
		if vil is None:
			vil = Village.objects.create()
			messages.info(request, "Village Created")
			con = None
			if request.user.is_superuser:
				con = Conference.objects.get(code=request.POST.get('code',False))
			else:
				con = get_user_conference(request)
			grp = Group.objects.create(name=con.code + ': ' + request.POST.get('village',False))
			for m in [Event, Speaker]:
				ct = ContentType.objects.get_for_model(model=m)
				perms = Permission.objects.filter(content_type=ct)
				for p in perms:
					grp.permissions.add(p)
		else:
			messages.info(request, "Village Updated")
		vil.village = request.POST.get('village',False)
		if request.user.is_superuser:
			con = Conference.objects.get(code=request.POST.get('code',False))
			vil.conference = con
		elif vil.conference is None:
			vil.conference = get_user_conference(request)
		vil.save()

		return redirect('/event_manager/village/' + str(vil.id) + '/')

	return render(
		request,
		'event_manager/village.html',
		{ 'vil': vil, 'cons': cons }
	)

# Authentication Views
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)

        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    # Redirect to a success page.
                    if user.is_superuser:
                        return redirect('select_con')
                    else:
                        return redirect('events')
        #else:
            #messages.info(request,"User does not exist")
        messages.info(request, "Login Failed")
        return render(request, 'event_manager/login.html', {})
    else:
    	return render(request, 'event_manager/login.html', {})

def logout_view(request):
    logout(request)
    return redirect('login')

# RESTful API

def events_json(request,code=None):
	all_events = None
	events_out = {}
	events_out['schedule'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_events = Event.objects.filter(conference=con)
	else:
		all_events = Event.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for e in all_events:
		e_dict = {'speakers':[]}
		e_dict['id'] = e.id
		e_dict['title'] = e.title
		e_dict['description'] = e.description
		e_dict['event_type'] = e.event_type.id
		if e.location is not None:
			e_dict['location'] = e.location.id
		else:
			e_dict['location'] = None
		e_dict['link'] = e.link
		e_dict['includes'] = e.includes
		e_dict['conference'] = e.conference.code
		for s in e.speakers.all():
			e_dict['speakers'].append(s.id)
		e_dict['start_date'] = datetime.datetime.strftime(e.start_date,'%Y-%m-%dT%H:%M%z')
		e_dict['end_date'] = datetime.datetime.strftime(e.end_date,'%Y-%m-%dT%H:%M%z')
		e_dict['updated_at'] = datetime.datetime.strftime(e.modified_date,'%Y-%m-%dT%H:%M%z')
		if e.modified_date > update_date: update_date = e.modified_date

		events_out['schedule'].append(e_dict)

	events_out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	events_json = json.dumps(events_out,indent=2)
	return HttpResponse(events_json,content_type='application/json')

def speakers_json(request,code=None):
	all_speakers = None
	speakers_out = {}
	speakers_out['speakers'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_speakers = Speaker.objects.filter(conference=con)
	else:
		all_speakers = Speaker.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for s in all_speakers:
		s_dict = {
			'id': s.id,
			'name': s.who,
			'title': s.sptitle,
			'description': s.bio,
			'twitter': s.twitter,
			'link': s.link,
			'conference': s.conference.code,
			'updated_at': datetime.datetime.strftime(s.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if s.modified_date > update_date: update_date = s.modified_date

		speakers_out['speakers'].append(s_dict)

	speakers_out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(speakers_out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def event_types_json(request,code=None):
	all_items = None
	out = {}
	out['event_types'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_items = EventType.objects.filter(conference=con)
	else:
		all_items = EventType.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for i in all_items:
		i_dict = {
			'id': i.id,
			'name': i.event_type,
			'color': i.color,
			'conference': i.conference.code,
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if i.modified_date > update_date: update_date = i.modified_date

		out['event_types'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def locations_json(request,code=None):
	all_items = None
	out = {}
	out['locations'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_items = Location.objects.filter(conference=con)
	else:
		all_items = Location.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for i in all_items:
		i_dict = {
			'id': i.id,
			'name': i.location,
			'hotel': i.hotel,
			'conference': i.conference.code,
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if i.modified_date > update_date: update_date = i.modified_date

		out['locations'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def vendors_json(request,code=None):
	all_items = None
	out = {}
	out['vendors'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_items = Vendor.objects.filter(conference=con)
	else:
		all_items = Vendor.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for i in all_items:
		i_dict = {
			'id': i.id,
			'name': i.title,
			'description': i.description,
			'link': i.link,
			'partner': i.partner,
			'conference': i.conference.code,
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if i.modified_date > update_date: update_date = i.modified_date

		out['vendors'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def articles_json(request,code=None):
	all_items = None
	out = {}
	out['articles'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_items = Article.objects.filter(conference=con)
	else:
		all_items = Article.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for i in all_items:
		i_dict = {
			'id': i.id,
			'name': i.name,
			'text': i.text,
			'conference': i.conference.code,
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if i.modified_date > update_date: update_date = i.modified_date

		out['articles'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def faqs_json(request,code=None):
	all_items = None
	out = {}
	out['faqs'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_items = FAQ.objects.filter(conference=con)
	else:
		all_items = FAQ.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for i in all_items:
		i_dict = {
			'id': i.id,
			'question': i.question,
			'answer': i.answer,
			'conference': i.conference.code,
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if i.modified_date > update_date: update_date = i.modified_date

		out['faqs'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def notifications_json(request,code=None):
	all_items = None
	out = {}
	out['notifications'] = []
	if code is not None:
		con = Conference.objects.get(code=code)
		all_items = Notification.objects.filter(conference=con)
	else:
		all_items = Notification.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	for i in all_items:
		i_dict = {
			'id': i.id,
			'text': i.text,
			'time': datetime.datetime.strftime(i.time,'%Y-%m-%dT%H:%M%z'),
			'conference': i.conference.code,
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		if i.modified_date > update_date: update_date = i.modified_date

		out['notifications'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')

def conferences_json(request):
	all_items = None
	out = {}
	out['conferences'] = []
	all_items = Conference.objects.all()
	update_date = datetime.datetime.strptime('2018-01-01T01:00+0000','%Y-%m-%dT%H:%M%z')
	base_link = 'https://hackertracker.app/'
	for i in all_items:
		i_dict = {
			'id': i.id,
			'name': i.name,
			'code': i.code,
			'description': i.description,
			'timezone': i.timezone,
			'link': i.link,
			'start_date': datetime.datetime.strftime(i.start_date,'%Y-%m-%d'),
			'end_date': datetime.datetime.strftime(i.end_date,'%Y-%m-%d'),
			'updated_at': datetime.datetime.strftime(i.modified_date,'%Y-%m-%dT%H:%M%z')
		}
		e = Event.objects.filter(conference=i).latest('modified_date')
		i_dict['events'] = {
			'updated_at': datetime.datetime.strftime(e.modified_date,'%Y-%m-%dT%H:%M%z'),
			'link': base_link + i.code + '/events.json'
			}
		et = EventType.objects.filter(conference=i).latest('modified_date')
		i_dict['event_types'] = {
			'updated_at': datetime.datetime.strftime(et.modified_date,'%Y-%m-%dT%H:%M%z'),
			'link': base_link + i.code + '/event_types.json'
			}
		s = Speaker.objects.filter(conference=i).latest('modified_date')
		i_dict['speakers'] = {
			'updated_at': datetime.datetime.strftime(s.modified_date,'%Y-%m-%dT%H:%M%z'),
			'link': base_link + i.code + '/speakers.json'
			}
		l = Location.objects.filter(conference=i).latest('modified_date')
		i_dict['locations'] = {
			'updated_at': datetime.datetime.strftime(l.modified_date,'%Y-%m-%dT%H:%M%z'),
			'link': base_link + i.code + '/locations.json'
			}
		if Vendor.objects.filter(conference=i):
			v = Vendor.objects.filter(conference=i).latest('modified_date')
			i_dict['vendors'] = {'updated_at': datetime.datetime.strftime(v.modified_date,'%Y-%m-%dT%H:%M%z') }
		else:
			i_dict['vendors'] = {'updated_at': '2018-01-01T01:00+0000' }

		i_dict['vendors']['link'] = base_link + i.code + '/vendors.json'

		if FAQ.objects.filter(conference=i):
			f = FAQ.objects.filter(conference=i).latest('modified_date')
			i_dict['faqs'] = {'updated_at': datetime.datetime.strftime(f.modified_date,'%Y-%m-%dT%H:%M%z') }
		else:
			i_dict['faqs'] = {'updated_at': '2018-01-01T01:00+0000' }
		i_dict['faqs']['link'] = base_link + i.code + '/faqs.json'

		if Notification.objects.filter(conference=i):
			n = Notification.objects.filter(conference=i).latest('modified_date')
			i_dict['notifications'] = {'updated_at': datetime.datetime.strftime(n.modified_date,'%Y-%m-%dT%H:%M%z') }
		else:
			i_dict['notifications'] = {'updated_at': '2018-01-01T01:00+0000' }
		i_dict['notifications']['link'] = base_link + i.code + '/notifications.json'

		if Article.objects.filter(conference=i):
			a = Article.objects.filter(conference=i).latest('modified_date')
			i_dict['articles'] = {'updated_at': datetime.datetime.strftime(a.modified_date,'%Y-%m-%dT%H:%M%z') }
		else:
			i_dict['articles'] = {'updated_at': '2018-01-01T01:00+0000' }
		i_dict['articles']['link'] = base_link + i.code + '/articles.json'

		if i.modified_date > update_date: update_date = i.modified_date

		out['conferences'].append(i_dict)

	out['updated_at'] = datetime.datetime.strftime(update_date,'%Y-%m-%dT%H:%M%z')
	json_out = json.dumps(out,indent=2)
	return HttpResponse(json_out,content_type='application/json')
