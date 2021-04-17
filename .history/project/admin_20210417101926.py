from django.contrib import admin

# Register your models here.
from .models import *
from django.contrib.sites.models import Site

class TraitTableAdmin(admin.ModelAdmin):
    list_display = ('trait_table',)

admin.site.register(Trait_Table)