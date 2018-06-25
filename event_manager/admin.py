from django.contrib import admin

from .models import Conference,EventType,Location,Vendor,Speaker,Event

admin.site.register(Conference)
admin.site.register(EventType)
admin.site.register(Location)
admin.site.register(Vendor)
admin.site.register(Speaker)
admin.site.register(Event)