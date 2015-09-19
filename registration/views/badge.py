from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from .utils import nopermission, get_or_404, is_involved

from ..models import Event, BadgeDesign, BadgePermission, BadgeRole
from ..forms import BadgeSettingsForm, BadgeDesignForm, BadgePermissionForm, \
    BadgeRoleForm


def notactive(request):
    return render(request, 'registration/admin/badges_not_active.html')


@login_required
def badges(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # permissions
    permissions = event.badge_settings.badgepermission_set.all()

    # roles
    roles = event.badge_settings.badgerole_set.all()

    context = {'event': event,
               'permissions': permissions,
               'roles': roles}
    return render(request, 'registration/admin/badges.html', context)


@login_required
def edit_badgesettings(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # form
    form = BadgeSettingsForm(request.POST or None, request.FILES or None,
                             instance=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badges', args=[event.url_name, ]))

    # render
    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgesettings.html',
                  context)


# TODO: join following 3 views
@login_required
def edit_badgedesign(request, event_url_name, design_pk=None, job_pk=None):
    event, job, shift, helper = get_or_404(event_url_name, job_pk)

    # check permission
    if not is_involved(request.user, event_url_name, admin_required=True):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgeDesign
    design = None
    if design_pk:
        design = get_object_or_404(BadgeDesign, pk=design_pk)

    # form
    form = BadgeDesignForm(request.POST or None, request.FILES or None,
                           instance=design)

    if form.is_valid():
        new_design = form.save()

        # add to job, if newly created
        if job_pk:
            job.badge_design = new_design
            job.save()
        return HttpResponseRedirect(reverse('badges', args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgedesign.html', context)


@login_required
def edit_badgepermission(request, event_url_name, permission_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    permission = None
    if permission_pk:
        permission = get_object_or_404(BadgePermission, pk=permission_pk)

        # check if permission belongs to event
        if permission not in event.badge_settings.badgepermission_set.all():
            return Http404()

    # form
    form = BadgePermissionForm(request.POST or None, instance=permission,
                               settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badges', args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgepermission.html',
                  context)


@login_required
def edit_badgerole(request, event_url_name, role_pk=None):
    event = get_object_or_404(Event, url_name=event_url_name)

    # check permission
    if not event.is_admin(request.user):
        return nopermission(request)

    # check if badge system is active
    if not event.badges:
        return notactive(request)

    # get BadgePermission
    role = None
    if role_pk:
        role = get_object_or_404(BadgeRole, pk=role_pk)

        # check if permission belongs to event
        if role not in event.badge_settings.badgerole_set.all():
            return Http404()

    # form
    form = BadgeRoleForm(request.POST or None, instance=role,
                         settings=event.badge_settings)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('badges', args=[event.url_name, ]))

    context = {'event': event,
               'form': form}
    return render(request, 'registration/admin/edit_badgerole.html',
                  context)