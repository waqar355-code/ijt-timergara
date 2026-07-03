from django.db import models

ELQA_CHOICES = [
    ('sindhakhall', 'Sindhakhall'),
    ('talash', 'Talash'),
    ('collage', 'Collage'),
    ('shaher', 'Shaher'),
    ('bazam', 'Bazam'),
    ('colleges', 'Colleges'),
]

MEMBER_TYPE_CHOICES = [
    ('karkun', 'کارکن'),
    ('rafiq', 'رفیق'),
    ('umeedwar', 'امیدوار'),
]

class Halqa(models.Model):
    elqa = models.CharField(max_length=50, choices=ELQA_CHOICES)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elqa} - {self.name}"


class Member(models.Model):
    elqa = models.CharField(max_length=50, choices=ELQA_CHOICES)
    halqa = models.ForeignKey(Halqa, on_delete=models.SET_NULL, null=True, blank=True)  # NEW
    name = models.CharField(max_length=200)
    member_type = models.CharField(max_length=20, choices=MEMBER_TYPE_CHOICES, default='karkun')  # NEW
    role = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elqa} - {self.name}"


class ElqaUpdate(models.Model):
    elqa = models.CharField(max_length=50, choices=ELQA_CHOICES)
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elqa} - {self.title}"





















































'''

from django.db import models

ELQA_CHOICES = [
    ('sindhakhall', 'Sindhakhall'),
    ('talash', 'Talash'),
    ('collage', 'Collage'),
    ('shaher', 'Shaher'),
    ('bazam', 'Bazam'),
    ('colleges', 'Colleges'),
]

class Halqa(models.Model):
    elqa = models.CharField(max_length=50, choices=ELQA_CHOICES)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elqa} - {self.name}"


class Member(models.Model):
    elqa = models.CharField(max_length=50, choices=ELQA_CHOICES)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elqa} - {self.name}"


class ElqaUpdate(models.Model):
    elqa = models.CharField(max_length=50, choices=ELQA_CHOICES)
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elqa} - {self.title}"
        
        '''
