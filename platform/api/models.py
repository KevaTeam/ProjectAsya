from django.utils.html import conditional_escape
from django.db import models
from datetime import datetime
from django.conf import settings

import random
import string

QUEST_ANSWER_LENGTH = 255


class Team(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        error_messages={
            'unique': 'The team with same name is already exists'
        }
    )

    token = models.CharField(max_length=255)
    score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.name = conditional_escape(self.name)

        super(Team, self).save(*args, **kwargs)


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

    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)

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

        self.name = conditional_escape(self.name)

        super(User, self).save(*args, **kwargs)


class QuestCategory(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        error_messages={
            'unique': 'The category with same name is already exists',
            'blank': 'Field name cannot be blank.',
        }
    )

    def __str__(self):
        return self.name

    def to_list(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def save(self, *args, **kwargs):
        self.name = conditional_escape(self.name)

        super(QuestCategory, self).save(*args, **kwargs)
        

class Quest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100)
    short_text = models.CharField(max_length=255)
    full_text = models.TextField()
    solution = models.TextField(blank=True)
    answer = models.CharField(max_length=QUEST_ANSWER_LENGTH)
    score = models.IntegerField()
    category = models.ForeignKey(QuestCategory, on_delete=models.CASCADE)
    tags = models.TextField(blank=True)

    def __str__(self):
        return "%s (%s)" % (
            self.name,
            self.category.name
        )

    def to_list(self):
        return {
            'id': self.id,
            'title': self.name,
            'author': self.author,
            'short_text': self.short_text,
            'full_text': self.full_text,
            'section': {
                'id': self.category.id,
                'title': self.category.name
            },
            'tags': self.tags.split(','),
            'score': self.score,
            'passed': bool(self.passed)
        }

    def save(self, *args, **kwargs):
        self.name = conditional_escape(self.name)
        self.author = conditional_escape(self.author)
        self.short_text = conditional_escape(self.short_text)
        self.full_text = conditional_escape(self.full_text)
        self.solution = conditional_escape(self.solution)
        self.tags = conditional_escape(self.tags)

        super(Quest, self).save(*args, **kwargs)
        
class UserQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
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
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=33)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
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
        
        self.user_answer = conditional_escape(self.user_answer)

        super(Attempt, self).save(*args, **kwargs)


class Message(models.Model):
    MESSAGE_TYPE = (
        (1, 'Для пользователя'),
        (2, 'Для всех')
    )
    type = models.IntegerField(default=1, choices=MESSAGE_TYPE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    time = models.DateTimeField('Дата создания новости')
    user = models.IntegerField(default=0)


class Config(models.Model):
    key = models.CharField(max_length=32, blank=False)
    value = models.CharField(max_length=255, blank=False)

    def as_datetime(self):
        try:
            d = datetime.strptime(self.value, '%d-%m-%Y %H:%M:%S')
        except ValueError:
            d = False

        return d
