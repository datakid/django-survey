from django.conf.urls.defaults import patterns, url

from views import answers_list, answers_detail,survey_detail

urlpatterns = patterns('',
    url(r'^(?P<survey_slug>[-\w]+)/answers/$', answers_list, name='survey-results'),
    url(r'^(?P<survey_slug>[-\w]+)/answers/(?P<key>[a-fA-F0-9]{10,40})/$', answers_detail, name='answers-detail'),
    url(r'^(?P<survey_slug>[-\w]+)/$', survey_detail,   name='survey-detail'),
    )
