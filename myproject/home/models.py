from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Contact(models.Model):
    firstName = models.CharField(max_length=122)
    lastName = models.CharField(max_length=122)
    email = models.EmailField(max_length=100)
    message = models.TextField(max_length=200)
    image = models.ImageField(upload_to="imag-contact")

class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Category for projects/gigs used for filtering."""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#client model
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

#project model
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="project-images")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name="projects")
    categories = models.ManyToManyField(Category, related_name='projects', blank=True)
    # Gig specific fields
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='USD')
    delivery_time = models.PositiveIntegerField(default=3, help_text='Delivery time in days')
    revisions = models.PositiveIntegerField(default=1)
    offers_consultation = models.BooleanField(default=False)
    rating = models.FloatField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    packages = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="projects")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Gig'
        verbose_name_plural = 'Gigs'

#experience model
class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"

#education model
class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

#user profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    about_me = models.TextField(blank=True)
    languages = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
