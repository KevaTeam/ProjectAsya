from django.db import models
from datetime import datetime
from django.conf import settings

import random
import string

QUEST_ANSWER_LENGTH = 255


class User(models.Model):
    name = models.CharField(
        "name",
        max_length=30,
        unique=True,
        blank=False,
        error_messages={
            'unique': 'The user with same username is already exists'
        }
    )
    mail = models.EmailField(
        "mail",
        blank=False
    )
    created_at = models.DateTimeField('Created date')
    # last_activity = models.DateTimeField('Date of last activity')
    rating = models.IntegerField(default=0)
    password = models.CharField(max_length=255)

    USER_ROLE = (
        (1, 'User'),
        (2, 'Administrator')
    )
    role = models.IntegerField(default=1, choices=USER_ROLE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.now()

        super(User, self).save(*args, **kwargs)


# Категории квестов
class Section(models.Model):
    name = models.CharField(max_length=30)


class Quest(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField()
    answer = models.CharField(max_length=QUEST_ANSWER_LENGTH)
    score = models.IntegerField()
    section = models.ForeignKey(Section)


class Token(models.Model):
    uid = models.ForeignKey(User)
    token = models.CharField(max_length=32)
    scope = models.IntegerField(default=1)
    ip = models.GenericIPAddressField()
    expires = models.DateTimeField()

    def generate(self, user, ip=None):
        self.uid = user
        self.token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(33))
        self.scope = user.role
        self.expires = datetime.now() + settings.TOKEN_EXPIRED_TIME
        self.ip = ip

class Attempt(models.Model):
    user = models.ForeignKey(User)
    quest = models.ForeignKey(Quest)
    user_answer = models.CharField(max_length=QUEST_ANSWER_LENGTH)

    # Почему мы записываем ответ задания постоянно?
    # Все просто. Во время игры ответ может измениться, а вердикт должен остаться
    task_answer = models.CharField(max_length=QUEST_ANSWER_LENGTH)

    time = models.DateTimeField()