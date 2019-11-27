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
	path('event_types/',views.event_types,name='event types'),
	path('event_types/<str:code>/',views.event_types,name='event type'),
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

	# Articles
	path('articles/',views.articles,name='articles'),
	path('articles/<str:code>/',views.articles,name='articles'),
	path('article/',views.article,name='add article'),
	path('article/<int:a_id>/',views.article,name='edit article'),
	path('article/d/<int:a_id>/',views.article_delete,name='delete article'),

	# FAQs
	path('faqs/',views.faqs,name='faqs'),
	path('faqs/<str:code>/',views.faqs,name='faqs'),
	path('faq/',views.faq,name='add faq'),
	path('faq/<int:f_id>/',views.faq,name='edit faq'),
	path('faq/d/<int:f_id>/',views.faq_delete,name='delete faq'),

	# Notifications
	path('notifications/',views.notifications,name='notifications'),
	path('notifications/<str:code>/',views.notifications,name='notifications'),
	path('notification/',views.notification,name='add notification'),
	path('notification/<int:n_id>/',views.notification,name='edit notification'),
	path('notification/d/<int:n_id>/',views.notification_delete,name='delete notification'),

	# Conferences
	path('conferences/',views.conferences,name='conferences'),
	path('conference/',views.conference),
	path('conference/select/',views.select_con,name='select_con'),
	path('conference/select/<str:code>/',views.select_con,name='select_con'),
	path('conference/<str:code>/',views.conference,name='conference'),
	path('conference/d/<str:code>/',views.conference_delete,name='delete conference'),

	# Authentication Endpoints
	path('login/', views.login, name='login'),
	path('logout/', views.logout_view, name='logout'),

	# JSON Endpoints
	path('api/conferences/',views.conferences_json,name='conferences json'),
	path('api/events/',views.events_json,name='events json'),
	path('api/events/<str:code>/',views.events_json,name='events json'),
	path('api/speakers/',views.speakers_json,name='speakers json'),
	path('api/speakers/<str:code>/',views.speakers_json,name='speakers json'),
	path('api/event_types/',views.event_types_json,name='event types json'),
	path('api/event_types/<str:code>/',views.event_types_json,name='event types json'),
	path('api/locations/',views.locations_json,name='locations'),
	path('api/locations/<str:code>/',views.locations_json,name='locations'),
	path('api/vendors/',views.vendors_json,name='vendors'),
	path('api/vendors/<str:code>/',views.vendors_json,name='vendors'),
	path('api/articles/',views.articles_json,name='articles'),
	path('api/articles/<str:code>/',views.articles_json,name='articles'),
	path('api/faqs/',views.faqs_json,name='faqs'),
	path('api/faqs/<str:code>/',views.faqs_json,name='faqs'),
	path('api/notifications/',views.notifications_json,name='notifications'),
	path('api/notifications/<str:code>/',views.notifications_json,name='notifications'),


	# Static files

	#path('api/',include(location_resource.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
