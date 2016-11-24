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

    def to_list(self):
        return {
            'id': self.id,
            'nick': self.name,
            'rating': self.rating,
            'passed': 0,
            'processing': 0
        }

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = datetime.now()

        super(User, self).save(*args, **kwargs)


class QuestCategory(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def to_list(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Quest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    answer = models.CharField(max_length=QUEST_ANSWER_LENGTH)
    score = models.IntegerField()
    category = models.ForeignKey(QuestCategory)

    def __str__(self):
        return "%s (%s)" % (
            self.name,
            self.category.name
        )

    def to_list(self):
        return {
            'id': self.id,
            'title': self.name,
            'text': self.text,
            'section': {
                'id': self.category.id,
                'title': self.category.name
            },
            'score': self.score,
            'passed': bool(self.passed)
        }


class UserQuest(models.Model):
    user = models.ForeignKey(User)
    quest = models.ForeignKey(Quest)
    begin = models.DateTimeField('Take time to quest')
    end = models.DateTimeField('Time delivery quest', blank=True, null=True)

    def __str__(self):
        return "User: %s. Quest: %s" % (
            self.user.name,
            self.quest.name
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.begin = datetime.now()

        super(UserQuest, self).save(*args, **kwargs)


class Token(models.Model):
    uid = models.ForeignKey(User)
    token = models.CharField(max_length=32)
    scope = models.IntegerField(default=1)
    ip = models.GenericIPAddressField()
    expires = models.DateTimeField()

    def generate(self, user, ip):
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
    quest_answer = models.CharField(max_length=QUEST_ANSWER_LENGTH)

    time = models.DateTimeField()

    def to_list(self):
        return {
            'user': {
                'id': self.user.id,
                'nick': self.user.name
            },
            'quest': {
                'title': self.quest.name,
                'section': self.quest.category.name
            },
            'user_answer': self.user_answer,
            'real_answer': self.quest_answer,
            'time': int(self.time.timestamp())
        }

    def save(self, *args, **kwargs):
        if not self.pk:
            self.time = datetime.now()

        super(Attempt, self).save(*args, **kwargs)


class Setting(models.Model):
    key = models.CharField(max_length=32, blank=False)
    value = models.CharField(max_length=255, blank=False)