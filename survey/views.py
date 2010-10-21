from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from survey.forms import forms_for_survey
from survey.models import Survey, Answer


def _survey_redirect(request, survey,
                    group_slug=None, group_slug_field=None, group_qs=None,
                    template_name = 'survey/thankyou.html',
                    extra_context=None,
                    *args, **kw):
    """
    Conditionally redirect to the appropriate page;
    if there is a "next" value in the GET URL parameter,
    go to the URL specified under Next.

    If there is no "next" URL specified, then go to
    the survey results page...but only if it is viewable
    by the user.

    Otherwise, only direct the user to a page showing
    their own survey answers...assuming they have answered
    any questions.

    If all else fails, go to the Thank You page.
    """
    if ('next' in request.REQUEST and
        request.REQUEST['next'].startswith('http:') and
        request.REQUEST['next'] != request.path):
        return HttpResponseRedirect(request.REQUEST['next'])
    if survey.answers_viewable_by(request.user):
        return HttpResponseRedirect(reverse('survey-results', None, (),
                                                {'survey_slug': survey.__dict__['slug_'+translation.get_language()]}))

    # For this survey, have they answered any questions?
    if (hasattr(request, 'session') and Answer.objects.filter(
            session_key=request.session.session_key.lower(),
            question__survey__visible=True,
            question__survey__slug=survey.slug).count()):
        return HttpResponseRedirect(
            reverse('answers-detail', None, (),
                    {'survey_slug': survey.__dict__['slug_'+translation.get_language()],
                     'key': request.session.session_key.lower()}))

    # go to thank you page
    return render_to_response(template_name,
                              {'survey': survey, 'title': _('Thank You')},
                              context_instance=RequestContext(request))

def survey_detail(request, survey_slug,
               group_slug=None, group_slug_field=None, group_qs=None,
               template_name = 'survey/survey_detail.html',
               extra_context=None,
               allow_edit_existing_answers=False,
               *args, **kw):
    """

    """
    filter_fields = {'visible': True, str('slug_' + translation.get_language())  : survey_slug }

    try:
        survey = Survey.objects.get(**filter_fields)
    except Survey.DoesNotExist:
        raise Http404

    if survey.template_name:
        template_name = survey.template_name
    if survey.closed:
        if survey.answers_viewable_by(request.user):
            return HttpResponseRedirect(reverse('survey-results', None, (),
                                                {'survey_slug': survey_slug}))
        raise Http404 #(_('Page not found.')) # unicode + exceptions = bad
    # if user has a session and have answered some questions
    # and the survey does not accept multiple answers,
    # go ahead and redirect to the answers, or a thank you
    if (hasattr(request, 'session') and
        survey.has_answers_from(request.session.session_key) and
        not survey.allows_multiple_interviews and not allow_edit_existing_answers):
        return _survey_redirect(request, survey,group_slug=group_slug)
    # if the survey is restricted to authentified user redirect
    # annonymous user to the login page
    if survey.restricted and str(request.user) == "AnonymousUser":
        return HttpResponseRedirect(reverse("auth_login")+"?next=%s" % request.path)
    if request.POST and not hasattr(request, 'session'):
        return HttpResponse(unicode(_('Cookies must be enabled.')), status=403)
    if hasattr(request, 'session'):
        skey = 'survey_%d' % survey.id
        request.session[skey] = (request.session.get(skey, False) or
                                 request.method == 'POST')
        request.session.modified = True ## enforce the cookie save.
    survey.forms = forms_for_survey(survey, request, allow_edit_existing_answers)
    if (request.POST and all(form.is_valid() for form in survey.forms)):
        for form in survey.forms:
            form.save()
        return _survey_redirect(request, survey,group_slug=group_slug)
    # Redirect either to 'survey.template_name' if this attribute is set or
    # to the default template
    return render_to_response(template_name,
                              {'survey': survey,
                               'title': survey.title,
                               'group_slug': group_slug},
                              context_instance=RequestContext(request))

def answers_list(request, survey_slug,
                 group_slug=None, group_slug_field=None, group_qs=None,
                 template_name = 'survey/answers_list.html',
                 extra_context=None,
                 *args, **kw):
    """
    Shows a page showing survey results for an entire survey.
    """
    filter_fields = {'visible': True, str('slug_' + translation.get_language())  : survey_slug }

    try:
        survey = Survey.objects.get(**filter_fields)
    except Survey.DoesNotExist:
        raise Http404
    # if the user lacks permissions, show an "Insufficient Permissions page"
    if not survey.answers_viewable_by(request.user):
        if (hasattr(request, 'session') and
            survey.has_answers_from(request.session.session_key)):
            return HttpResponseRedirect(
                reverse('answers-detail', None, (),
                        {'survey_slug': survey.slug,
                         'key': request.session.session_key.lower()}))
        return HttpResponse(unicode(_('Insufficient Privileges.')), status=403)
    return render_to_response(template_name,
        { 'survey': survey,
          'view_submissions': request.user.has_perm('survey.view_submissions'),
          'title': survey.title + u' - ' + unicode(_('Results'))},
        context_instance=RequestContext(request))



def answers_detail(request, survey_slug, key,
                   group_slug=None, group_slug_field=None, group_qs=None,
                   template_name = 'survey/answers_detail.html',
                   extra_context=None,
                   *args, **kw):
    """
    Shows a page with survey results for a single person.

    If the user lacks permissions, show an "Insufficient Permissions page".
    """
    filter_fields = {'session_key':key.lower(), 'question__survey__visible':True, str('question__survey__slug_'+translation.get_language()): survey_slug, 'visible': True,  }

    answers = Answer.objects.filter(**filter_fields).order_by('question__order')
    if not answers.count(): raise Http404
    survey = answers[0].question.survey

    mysubmission = (hasattr(request, 'session') and
         request.session.session_key.lower() == key.lower())

    if (not mysubmission and
        (not request.user.has_perm('survey.view_submissions') or
         not survey.answers_viewable_by(request.user))):
        return HttpResponse(unicode(_('Insufficient Privileges.')), status=403)
    return render_to_response(template_name,
        {'survey': survey, 'submission': answers,
         'title': survey.title + u' - ' + unicode(_('Submission')), 'key':key.lower() },
        context_instance=RequestContext(request))

