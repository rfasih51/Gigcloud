from django.contrib import admin
from home.models import Contact
from .models import Project, Skill, Client


# Register your models here.
admin.site.register(Contact)
admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(Client)

# Register additional models
from .models import Experience, Education, UserProfile, Category

admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(UserProfile)
admin.site.register(Category)

