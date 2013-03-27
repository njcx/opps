# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from googl.short import GooglUrlShort

from opps.core.models import Publishable


class Article(Publishable):
    title = models.CharField(_(u"Title"), max_length=140)
    headline = models.TextField(_(u"Headline"), blank=True)
    slug = models.SlugField(
        _(u"URL"),
        db_index=True,
        max_length=150,
        unique=True,
    )
    short_title = models.CharField(
        _(u"Short title"),
        max_length=140,
        null=True, blank=False,
    )
    short_url = models.URLField(
        _("Short URL"),
        null=True, blank=False,
    )
    channel = models.ForeignKey(
        'channels.Channel',
        verbose_name=_(u"Channel"),
    )
    main_image = models.ForeignKey(
        'images.Image',
        null=True, blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_(u'Main Image'),
    )
    images = models.ManyToManyField(
        'images.Image',
        null=True, blank=True,
        related_name='article_images',
        through='articles.ArticleImage',
    )
    sources = models.ManyToManyField(
        'sources.Source',
        null=True, blank=True,
        through='articles.ArticleSource',
    )
    tags = TagField(null=True, verbose_name=_(u"Tags"))

    def __unicode__(self):
        return self.__absolute_url()

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = GooglUrlShort(self.get_absolute_url()).short()
        super(Article, self).save(*args, **kwargs)

    def __absolute_url(self):
        return "{0}/{1}".format(self.channel, self.slug)

    def get_absolute_url(self):
        return "http://{0}".format(self.__absolute_url())
    get_absolute_url.short_description = 'URL'


class Post(Article):
    content = models.TextField(_(u"Content"))
    album = models.ManyToManyField(
        'articles.Album',
        null=True, blank=True,
        related_name='post_albums',
    )


class Album(Article):
    pass


class ArticleSource(models.Model):
    article = models.ForeignKey(
        'articles.Article',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='articlesource_articles',
        verbose_name=_(u'Article'),
    )
    source = models.ForeignKey(
        'sources.Source',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='articlesource_sources',
        verbose_name=_(u'Source'),
    )
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return self.source.slug


class ArticleImage(models.Model):
    article = models.ForeignKey(
        'articles.Article',
        verbose_name=_(u'Article'),
        null=True, blank=True,
        related_name='articleimage_articles',
        on_delete=models.SET_NULL
    )
    image = models.ForeignKey(
        'images.Image',
        verbose_name=_(u'Image'),
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return self.image.title


class ArticleBox(Publishable):
    name = models.CharField(_(u"Box name"), max_length=140)
    slug = models.SlugField(
        _(u"Slug"),
        db_index=True,
        max_length=150,
        unique=True,
    )
    article = models.ForeignKey(
        'articles.Article',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    channel = models.ForeignKey(
        'channels.Channel',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    articles = models.ManyToManyField(
        'articles.Article',
        null=True, blank=True,
        related_name='articlebox_articles',
        through='articles.ArticleBoxArticles'
    )

    def __unicode__(self):
        return self.slug


class ArticleBoxArticles(models.Model):
    articlebox = models.ForeignKey(
        'articles.ArticleBox',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='articleboxarticles_articleboxes',
        verbose_name=_(u'Article Box'),
    )
    article = models.ForeignKey(
        'articles.Article',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='articleboxarticles_articles',
        verbose_name=_(u'Article'),
    )
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return "{0}-{1}".format(self.articlebox.slug, self.article.slug)
