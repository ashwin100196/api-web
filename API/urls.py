from django.conf.urls import url
from API import views

urlpatterns = [
	url(r'^alerthistory/$',views.alert_history),
	url(r'^alerts/$',views.get_mainpage),
	url(r'^snippets/$',views.snippet_list),
	url(r'^snippets/(?P<pk>[0-9]+)/$',views.snippet_detail),\
]