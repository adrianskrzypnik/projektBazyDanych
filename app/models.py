from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    haslo = models.CharField(max_length=255)
    data_utworzenia = models.DateField()

    class Meta:
        managed = False
        db_table = 'users'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'categories'

class Ad(models.Model):
    ad_id = models.AutoField(primary_key=True)
    tytul = models.CharField(max_length=255)
    opis = models.TextField(null=True, blank=True)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    kategoria = models.ForeignKey(Category, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    data_utworzenia = models.DateField()

    class Meta:
        managed = False
        db_table = 'categories'

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    ogloszenie = models.ForeignKey(Ad, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    tresc = models.TextField()
    data_utworzenia = models.DateField()

    class Meta:
        managed = False
        db_table = 'comments'

class Like(models.Model):
    like_id = models.AutoField(primary_key=True)
    ogloszenie = models.ForeignKey(Ad, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    polubiony_przez = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'likes'

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    oceniający = models.ForeignKey(User, related_name='oceniajacy', on_delete=models.CASCADE)
    oceniany = models.ForeignKey(User, related_name='oceniany', on_delete=models.CASCADE)
    ocena = models.IntegerField()
    data_oceny = models.DateField()

    class Meta:
        managed = False
        db_table = 'ratings'
