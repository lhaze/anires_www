from datetime import date

from django.db import models
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponse

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailsearch import index

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from anires.core.models import RelatedLink, CarouselItem


# Blog index page

class IndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('IndexPage', related_name='related_links')


class IndexPage(Page):
    intro = RichTextField(blank=True)

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
    )

    @property
    def entries(self):
        # Get list of live blog pages that are descendants of this page
        entries = EntryPage.objects.live().descendant_of(self).order_by('-date')
        return entries

    def get_context(self, request):
        entries = self.entries

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            entries = entries.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(entries, settings.ENTRIES_PER_PAGE_COUNT)
        try:
            entries = paginator.page(page)
        except PageNotAnInteger:
            entries = paginator.page(1)
        except EmptyPage:
            entries = paginator.page(paginator.num_pages)

        # Update template context
        context = super(IndexPage, self).get_context(request)
        context['entries'] = entries
        return context

IndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel(IndexPage, 'related_links', label="Related links"),
]
IndexPage.promote_panels = Page.promote_panels


class EntryPage(Page):
    body = RichTextField()
    tags = ClusterTaggableManager(through='EntryTag', blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    @property
    def index_page(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(IndexPage).last()

EntryPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('body', classname="full"),
    InlinePanel(EntryPage, 'carousel_items', label="Carousel items"),
    InlinePanel(EntryPage, 'related_links', label="Related links"),
]
EntryPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]


class EntryTag(TaggedItemBase):
    content_object = ParentalKey(EntryPage, related_name='tagged_items')


class EntryRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('news.EntryPage', related_name='related_links')


class EntryCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('news.EntryPage', related_name='carousel_items')
