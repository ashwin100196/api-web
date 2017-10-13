from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from API.models import Alert
from API.serializers import AlertSerializer
import time

# Create your views here.

import json
from pymongo import MongoClient
client = MongoClient('mongodb://heroku_z9l8tf4w:g3l5j5hbh755td1sm8e0pf30er@ds117605.mlab.com:17605/heroku_z9l8tf4w')
db = client.get_database()
alerts = db.alarm_history

def sum_the_time(cursor,time_start,time_end):
	temp_time = time_start
	sum=0.0
	for alarm in cursor:
		if alarm['condition']:
			temp_time = alarm['timestamp']
		else:
			sum += alarm['timestamp']-temp_time
			temp_time = alarm['timestamp']
	return sum

def alert_history(request):
	query = request.GET.get('query','not')
	location_id = request.GET.get('l-id','1')
	cctv_id = request.GET.get('cc-id','1')
	event_type = request.GET.get('type','all')
	time_start = request.GET.get('t-start',time.time()-86400.0)
	time_end = request.GET.get('t-end',time.time())
	if query == 'alert-history':
		if event_type == 'all':
			cursor = alerts.find({"$and":[{"alert":"True"},{"type":"person"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
			c1 = cursor.count()
			sum1 = sum_the_time(cursor,time_start,time_end)
			cursor = alerts.find({"$and":[{"alert":"True"},{"type":"hardhat"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
			c2 = cursor.count()
			sum2 = sum_the_time(cursor,time_start,time_end)
			cursor = alerts.find({"$and":[{"alert":"True"},{"type":"safetyglasses"},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
			c3 = cursor.count()
			sum3 = sum_the_time(cursor,time_start,time_end)
			t_sum = sum1+sum2+sum3
			alert_piechart_p1 = sum1/t_sum*100.0
			alert_piechart_p2 = sum2/t_sum*100.0
			alert_piechart_p3 = sum3/t_sum*100.0
			true_alerts = c1+c2+c3
			total_alerts = alerts.find({"timestamp":{"$gt":time_start,"$lt":time_end}}).count()
			false_percentage = (1-(true_alerts/total_alerts))*100.0
			resp_data = {"Percentage1":alert_piechart_p1,"Percentage2":alert_piechart_p2,"Percentage3":alert_piechart_p3, "False alert percentage" : false_percentage}
			return JsonResponse(resp_data)
		else:
			cursor = alerts.find({"$and":[{"alert":"True"},{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]})
			true_alerts = cursor.count()
			sum = sum_the_time(cursor,time_start,time_end)
			piechart_percentage = sum/86400*100.0
			total_alerts = alerts.find({"$and":[{"type":event_type},{"timestamp":{"$gt":time_start,"$lt":time_end}}]}).count()
			false_percentage = (1-(true_alerts/total_alerts))*100
			resp_data = {"Percentage":piechart_percentage,"False alert percentage":false_percentage}
			return JsonResponse(resp_data)
	else:
		return HttpResponse(status=404)

#@csrf_exempt
def get_mainpage(request):
	new_time = time.time()
	old_time = new_time - 86400.0
	query = request.GET.get('query','not')
	if query =='start':
		cursor = alerts.find({"$and":[{"alert":"True"},{"timestamp":{"$gt":old_time,"$lt":new_time}}]})
		#for alarm in cursor:
			#if alarm['condition']:
				#sum_time += alarm['timestamp']-temp_time
				#temp_time = alarm['timestamp']
			#else:
				#temp_time = alarm['timestamp']
		sum_time = sum_the_time(cursor,old_time,new_time)
		Mainchart_percentage = sum_time/86400.0*100
		person_detected = 0
		hardhat_missing = 0
		safetyglasses_missing = 0
		cursor = alerts.find({"$and":[{"alert":"True"},{"type":"person"}]} ).sort([("$natural" , -1)]).limit(1);
		for alarm in cursor:
			if alarm['condition']:
				person_detected = 1
		cursor = alerts.find( {"$and":[{"alert":"True"},{"type":"hardhat"}]} ).sort([("$natural" , -1)]).limit(1);
		for alarm in cursor:
			if alarm['condition']:
				hardhat_missing = 1
		cursor = alerts.find( {"$and":[{"alert":"True"},{"type":"safetyglasses"}]} ).sort([("$natural" , -1)]).limit(1);
		for alarm in cursor:
			if alarm['condition']:
				safetyglasses_missing = 1
		resp_data = {"Piechart":Mainchart_percentage,"person":person_detected,"hardhat":hardhat_missing,"safetyglasses":safetyglasses_missing}
		return JsonResponse(resp_data)
	else:
		return HttpResponse(status=404)

@csrf_exempt
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
		
		
@csrf_exempt
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)