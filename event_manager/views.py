#
# HackerTracker Event Manager
#
# created_by: @sethlaw

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import json
import re

from .models import Event, Location, EventType, Speaker, Vendor, Village, Conference

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
def conferences(request):
	if request.user.is_superuser: 
		conferences = list(Conference.objects.all())
		return render(
			request,
			'event_manager/conferences.html',
			{ 'conferences': conferences }
		)
	else:
		return redirect('/event_manager/events/')
	
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
					messages.warn(request,"Conference Code already exists")
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
		return redirect('/event_manager/events/')

@login_required
def events(request,code=None):
	event_list = []
	if code is not None: 
		con = Conference.objects.get(code=code)
		event_list = list(Event.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		event_list = list(Event.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Event.objects.filter(conference=c):
				event_list.append(e)
		
	return render(
		request,
		'event_manager/events.html',
		{ 'event_list': event_list }
	)

@login_required
def event_delete(request,e_id=None):
	if not request.user.is_superuser or not request.user.is_staff:
		messages.warn(request,"Unauthorized")
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
		for s_sp in s_speakers:
			sp = Speaker.objects.get(id=s_sp)
			e.speakers.add(sp)
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
		if code is not None: 
			con = Conference.objects.get(code=code)
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
		return redirect('/event_manager/events/')

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
	
	if request.method == 'DELETE':
		et_type.delete()
		messages.info(request, "Event Type Deleted")
		return redirect('/event_manager/event_types/')
	
	if request.method == 'POST':
		if et_type is None:
			et_type = EventType.objects.create()
			messages.info(request, "Event Type Created")
		else:
			messages.info(request, "Event Type Updated")
		et_type.event_type = request.POST.get('event_type',False)
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
	if code is not None: 
		con = Conference.objects.get(code=code)
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
	if code is not None: 
		con = Conference.objects.get(code=code)
		sp_list = list(Speaker.objects.filter(conference=con))
	elif request.user.is_superuser:
		con = None
		sp_list = list(Speaker.objects.all())
	else:
		for grp in request.user.groups.all():
			c = Conference.objects.get(code=grp.name)
			for e in Speaker.objects.filter(conference=c):
				sp_list.append(e)
		
	return render(
		request,
		'event_manager/speakers.html',
		{ 'speakers': sp_list }
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
	if code is not None: 
		con = Conference.objects.get(code=code)
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
			print('PAR: '+ str(par))
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

# Villages
@login_required
def villages(request,code=None):
	vil_list = []
	if code is not None: 
		con = Conference.objects.get(code=code)
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
                    return redirect('/event_manager/events/')
        else:
            messages.info(request,"User does not exist")
        messages.info(request, "Login Failed")
        return render(request, 'event_manager/login.html', {})
    else:
    	return render(request, 'event_manager/login.html', {})

def logout_view(request):
    logout(request)
    return redirect('/event_manager/login/')

# RESTful API

@login_required
def event_edit(request, event_id):
	try:
		event = Event.objects.get(id=event_id)
	except:
		raise Http404("Event does not exist")

	if request.method == 'GET':
		return HttpResponse("You're looking at event %s" % event_id)
	elif request.method == 'PUT':
		return HttpResponse("You're updating the event %s" % event_id)

@login_required
def location_json(request):
	locations = Location.objects.all().values('location')
	locations_json = json.dumps(list(locations))
	return HttpResponse(locations_json, content_type='application/json')

@login_required
def vendors_json(request):
	vendors = Vendor.objects.all()
	vendors_json = json.dumps(list(vendors))
	return HttpResponse(vendors_json, content_type='application/json')
