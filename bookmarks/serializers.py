from django.core import serializers
from django.db.models.loading import get_model
from django.http import HttpResponse

def bookmarks_json(request, model_name, object_id=None):
    if object_id==None:
        data = serializers.serialize("json", get_model("bookmarks", model_name).objects.all())
    else:
        data = serializers.serialize("json", get_model("bookmarks", model_name).objects.filter(id=object_id))
    return HttpResponse(data, mimetype="application/javascript")

def bookmarks_xml(request, model_name, object_id=None):
    if object_id==None:
        data = serializers.serialize("xml", get_model("bookmarks", model_name).objects.all())
    else:
        data = serializers.serialize("xml", get_model("bookmarks", model_name).objects.filter(id=object_id))
    return HttpResponse(data, mimetype="application/xml")

