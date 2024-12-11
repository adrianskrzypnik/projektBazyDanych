from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, nazwa, haslo=None):
        if not email:
            raise ValueError('Użytkownik musi mieć adres email')

        user = self.model(
            email=self.normalize_email(email),
            nazwa=nazwa
        )
        user.set_password(haslo)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nazwa, haslo=None):
        user = self.create_user(
            email=email,
            nazwa=nazwa,
            haslo=haslo
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    data_utworzenia = models.DateField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nazwa']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

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
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)#uzytkownik ktory dal komentarz
    tresc = models.TextField()
    data_utworzenia = models.DateField()

    class Meta:
        managed = False
        db_table = 'comments'

class Like(models.Model):
    like_id = models.AutoField(primary_key=True)
    ogloszenie = models.ForeignKey(Ad, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)#uzytkownik ktory dal polubienie

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

