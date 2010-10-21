from survey.models import Answer, Choice, Question, Survey
from django.contrib import admin

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    exclude = ('image', )
    template = 'admin/survey/choice/edit_inline_tabular.html'

class QuestionOptions(admin.ModelAdmin):
    list_select_related = True
    list_filter = ('survey', 'qtype')
    list_display_links = ('text',)
    list_display = ('survey', 'text', 'qtype', 'required')
    search_fields = ('text',)
    inlines = [ ChoiceInline, ]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 4
    exclude = ('qstyle', 'required', 'image', 'choice_num_min', 'choice_num_max', )
    template = 'admin/survey/question/edit_inline_tabular.html'

class SurveyOptions(admin.ModelAdmin):
    prepopulated_fields = {'slug_en': ('title_en',)}
    list_display = ('__unicode__', 'visible', 'public',
                        'opens', 'closes', 'open')
    inlines = [QuestionInline]

class AnswerOptions(admin.ModelAdmin):
    list_display = ('interview_uuid','question','user', 'submission_date',
                    'session_key', 'text')
    #list_filter = ('question__survey',)
    search_fields = ('text',)
    list_select_related=True

class ChoiceOptions(admin.ModelAdmin):
    list_display = ('question','text',)
    search_fields = ('text',)
    list_filter = ('question',)


admin.site.register(Question, QuestionOptions)
admin.site.register(Survey, SurveyOptions)
admin.site.register(Answer, AnswerOptions)
admin.site.register(Choice, ChoiceOptions)
