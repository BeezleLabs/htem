from django.urls import include,path, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
	path('',views.index,name='index'),
	# UI Endpoints
	path('dashboard/',views.dashboard,name='dashboard'),
	# Events
	path('events/',views.events,name='events'),
	path('events/<str:code>/',views.events,name='events'),
	path('event/',views.event,name='add event'),
	path('event/<int:e_id>/',views.event,name='edit event'),
	path('event/d/<int:e_id>/',views.event_delete,name='delete event'),
	
	# Event Types
	path('event_types/',views.event_types,name='events'),
	path('event_types/<str:code>/',views.event_types,name='events'),
	path('event_type/',views.event_type,name='add event_types'),
	path('event_type/<int:et_id>/',views.event_type,name='edit event type'),
	path('event_type/d/<int:et_id>/',views.event_type_delete,name='delete event type'),
	
	# Locations
	path('locations/',views.locations,name='locations'),
	path('locations/<str:code>/',views.locations,name='locations'),
	path('location/',views.location,name='add location'),
	path('location/<int:loc_id>/',views.location,name='edit location'),
	path('location/d/<int:loc_id>/',views.location_delete,name='delete location'),
	
	# Speakers
	path('speakers/',views.speakers,name='speakers'),
	path('speakers/<str:code>/',views.speakers,name='speakers'),
	path('speaker/',views.speaker,name='add speaker'),
	path('speaker/<int:sp_id>/',views.speaker,name='edit speaker'),
	path('speaker/d/<int:sp_id>/',views.speaker_delete,name='delete speaker'),
	
	# Vendors
	path('vendors/',views.vendors,name='vendors'),
	path('vendors/<str:code>/',views.vendors,name='vendors'),
	path('vendor/',views.vendor,name='add vendor'),
	path('vendor/<int:v_id>/',views.vendor,name='edit vendor'),
	path('vendor/d/<int:v_id>/',views.vendor_delete,name='delete vendor'),
	
	# Villages
	path('villages/',views.villages,name='villages'),
	path('villages/<str:code>/',views.villages,name='villages'),
	path('village/',views.village,name='add village'),
	path('village/<int:vil_id>/',views.village,name='edit village'),
	path('village/d/<int:vil_id>/',views.village_delete,name='delete village'),
	
	# Conferences
	path('conferences/',views.conferences,name='conferences'),
	path('conference/',views.conference),
	path('conference/<str:code>/',views.conference,name='conference'),
	path('conference/d/<str:code>/',views.conference_delete,name='delete conference'),

	# Authentication Endpoints
	path('login/', views.login, name='login'),
	path('logout/', views.logout_view, name='logout'),

	# JSON Endpoints
	path('api/event/<int:event_id>/',views.event_edit,name='event edit'),
	
	path('api/location/',views.location_json,name='locations'),
	path('api/vendor/',views.vendors_json,name='vendors'),

	# Static files

	#path('api/',include(location_resource.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
