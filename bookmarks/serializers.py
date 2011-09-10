from django.core import serializers
from django.db.models.loading import get_model
from django.http import HttpResponse


def bookmarks_json(request, model_name, object_id=None):
    model = get_model("bookmarks", model_name)
    if object_id is None:
        bookmarks = model.objects.all()
    else:
        bookmarks = model.objects.filter(id=object_id)
    data = serializers.serialize("json", bookmarks)
    return HttpResponse(data, mimetype="application/javascript")


def bookmarks_xml(request, model_name, object_id=None):
    model = get_model("bookmarks", model_name)
    if object_id is None:
        bookmarks = model.objects.all()
    else:
        bookmarks = model.objects.filter(id=object_id)
    data = serializers.serialize("json", bookmarks)
    return HttpResponse(data, mimetype="application/xml")
