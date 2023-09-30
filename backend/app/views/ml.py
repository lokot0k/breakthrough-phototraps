import os
import shutil

from django.core.files.base import ContentFile
from django.db import models
from django.forms import forms
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
import zipfile
import csv
from PIL import Image

from app.models.ml_model import generate_submission_folder, model
from app.utils.storage import MyStorage


class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a file')


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/abc.zip')


class MlView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        storage = MyStorage()
        empty_list = []
        good_list = []
        bad_list = []
        with open(storage.path('submission.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if row[1] == "1":
                    bad_list.append(f"/media/{row[0]}")
                elif row[2] == "1":
                    empty_list.append(f"/media/{row[0]}")
                elif row[3] == "1":
                    good_list.append(f"/media/{row[0]}")

        # return JsonResponse(
        #     {"success": True, "empty": empty_list, "animal": good_list,
        #      "broken": bad_list, "csv": f"/media/submission.csv"})
        return JsonResponse({"empty": empty_list, "animal": good_list,
                             "broken": bad_list})

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            requ = request.FILES['docfile']
            storage = MyStorage()
            shutil.rmtree(settings.MEDIA_ROOT)
            settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
            path = storage.save('abc.zip',
                                ContentFile(requ.read()))


            # разархивировать по path, грузануть в медиа. Собрать .csv в едины жсон респонс.
            with zipfile.ZipFile(path,  # выгрузка
                                 "r") as zip:
                zip.extractall(settings.MEDIA_ROOT)

            directory = os.fsencode(settings.MEDIA_ROOT)

            generate_submission_folder([model],
                                       settings.MEDIA_ROOT)  # вот эта строчка пример юзания
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.lower().endswith(
                        ".png") or filename.lower().endswith(
                    ".jpg") or filename.lower().endswith(".jpeg"):
                    try:
                        img = Image.open(storage.path(filename))
                        x, y = img.size
                        if x > 600 and y > 800:
                            x = x // 2
                            y = y // 2
                            img = img.resize((x, y), Image.ANTIALIAS)
                        img.save(storage.path(filename), quality=90)
                    except:
                        pass
            empty_list = []
            good_list = []
            bad_list = []

            paths = ["a/", "b/", "e/", "ab/", "ae/", "be/", "abe/"]

            for path in paths:
                (settings.MEDIA_ROOT / path).mkdir(parents=True, exist_ok=True)
            with open(storage.path('submission.csv'), 'r') as f:
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    print(row)
                    if not row or len(row) != 4:
                        continue
                    if row[1] == "1":
                        bad_list.append(f"/media/{row[0]}")
                        for path in paths:
                            if 'b' in path:
                                shutil.copy(storage.path(row[0]), storage.path(path + row[0]))
                    elif row[2] == "1":
                        empty_list.append(f"/media/{row[0]}")
                        for path in paths:
                            if 'e' in path:
                                shutil.copy(storage.path(row[0]), storage.path(path + row[0]))
                    elif row[3] == "1":
                        good_list.append(f"/media/{row[0]}")
                        for path in paths:
                            if 'a' in path:
                                shutil.copy(storage.path(row[0]), storage.path(path + row[0]))

            for path in paths:
                shutil.make_archive(storage.path(path), "zip", storage.path(path))

            return JsonResponse(
                {"success": "true", "empty": empty_list, "animal": good_list,
                 "broken": bad_list, "csv": f"/media/submission.csv"})
        else:
            return JsonResponse({"success": "false", "message": "плохо"},
                                status=403)

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'me ssage': 'unsupported method'}, status=403)
