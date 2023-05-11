from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _

from pretalx.orga.signals import nav_event


@receiver(nav_event, dispatch_uid='halfnarp')
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_perm('orga.view_submissions', request.event):
        return []
    return [{
        'label': _('Halfnarp'),
        'icon': 'thumbs-up',
        'url': reverse('plugins:pretalx_halfnarp:organiser', kwargs={
            'event': request.event.slug,
        }),
        'active': url.namespace == 'plugins:pretalx_halfnarp' and url.url_name == 'view',
    }]
