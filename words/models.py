from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class GroupOfWords(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Words(models.Model):
    name = models.CharField(max_length=255)
    ru_name = models.CharField(max_length=255)
    value = models.TextField(blank=True)
    example = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)
    group = models.ForeignKey(GroupOfWords, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_words_time = models.DateTimeField(default=timezone.now,
                                          auto_now=False,
                                          auto_now_add=False,
                                          null=True,
                                          blank=True)
    bad_words = models.ManyToManyField(Words,
                                       blank=True,
                                       related_name='user_bad_words')
    good_words = models.ManyToManyField(Words,
                                        blank=True,
                                        related_name='user_good_words')
    new_words = models.ManyToManyField(Words,
                                       blank=True,
                                       related_name='user_new_words')
    added_words = models.ManyToManyField(Words,
                                         blank=True,
                                         related_name='added_words')

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class UserOldWords(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Words, on_delete=models.CASCADE)
    word_count = models.IntegerField(default=1)
    word_update = models.DateTimeField(auto_now=False,
                                       auto_now_add=False,
                                       null=True,
                                       blank=True)

    def __str__(self):
        return "word: {} - user:{}".format(self.word.name, self.user.username)
