import os
import shutil
from django.core.files import locks
from django.core.files.base import ContentFile, File
from django.core.files.move import file_move_safe
from django.db import models
from django.forms import forms
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View
from django.core.files.storage import DefaultStorage
from django.conf import settings
import zipfile
import csv
from PIL import Image


class MyStorage(DefaultStorage):
    def _save(self, name, content):
        full_path = self.path(name)
        # Create any intermediate directories that do not exist.
        directory = os.path.dirname(full_path)
        try:
            if self.directory_permissions_mode is not None:
                # Set the umask because os.makedirs() doesn't apply the "mode"
                # argument to intermediate-level directories.
                old_umask = os.umask(0o777 & ~self.directory_permissions_mode)
                try:
                    os.makedirs(
                        directory, self.directory_permissions_mode,
                        exist_ok=True
                    )
                finally:
                    os.umask(old_umask)
            else:
                os.makedirs(directory, exist_ok=True)
        except FileExistsError:
            raise FileExistsError(
                "%s exists and is not a directory." % directory)

        while True:
            try:
                # This file has a file path that we can move.
                if hasattr(content, "temporary_file_path"):
                    file_move_safe(content.temporary_file_path(), full_path,
                                   allow_overwrite=True)

                # This is a normal uploadedfile that we can stream.
                else:
                    # The current umask value is masked out by os.open!
                    fd = os.open(full_path, self.OS_OPEN_FLAGS, 0o666)
                    _file = None
                    try:
                        locks.lock(fd, locks.LOCK_EX)
                        for chunk in content.chunks():
                            if _file is None:
                                mode = "wb" if isinstance(chunk,
                                                          bytes) else "wt"
                                _file = os.fdopen(fd, mode)
                            _file.write(chunk)
                    finally:
                        locks.unlock(fd)
                        if _file is not None:
                            _file.close()
                        else:
                            os.close(fd)
            except FileExistsError:
                # A new name is needed if the file exists.
                full_path = self.path(name)
                os.remove(full_path)
                fd = os.open(full_path, self.OS_OPEN_FLAGS, 0o666)
                _file = None
                try:
                    locks.lock(fd, locks.LOCK_EX)
                    for chunk in content.chunks():
                        if _file is None:
                            mode = "wb" if isinstance(chunk, bytes) else "wt"
                            _file = os.fdopen(fd, mode)
                        _file.write(chunk)
                finally:
                    locks.unlock(fd)
                    if _file is not None:
                        _file.close()
                    else:
                        os.close(fd)
                    break
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if self.file_permissions_mode is not None:
            os.chmod(full_path, self.file_permissions_mode)

        # Ensure the saved path is always relative to the storage root.
        name = full_path
        # Ensure the moved file has the same gid as the storage root.
        self._ensure_location_group_id(full_path)
        # Store filenames with forward slashes, even on Windows.
        return str(name).replace("\\", "/")

    def save(self, name, content):
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, "chunks"):
            content = File(content, name)
        shutil.rmtree(settings.MEDIA_ROOT)
        name = self._save(name, content)
        return name


class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a file')


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/abc.zip')


class MlView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            requ = request.FILES['docfile']
            storage = MyStorage()
            path = storage.save('abc.zip',
                                ContentFile(requ.read()))
            # разархивировать по path, грузануть в медиа. Собрать .csv в едины жсон респонс.
            with zipfile.ZipFile(path,  # выгрузка
                                 "r") as zip:
                zip.extractall(settings.MEDIA_ROOT)

            directory = os.fsencode(settings.MEDIA_ROOT)

            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.endswith(".png") or filename.endswith(
                        ".jpg") or filename.endswith(".jpeg"):
                    img = Image.open(storage.path(filename))
                    x, y = img.size
                    if x > 600 and y > 800:
                        x = x // 2
                        y = y // 2
                        img = img.resize((x, y), Image.ANTIALIAS)
                    img.save(storage.path(filename), quality=90)
            empty_list = []
            good_list = []
            bad_list = []
            with open(storage.path('result.csv'), 'r') as f:
                reader = csv.reader(f, delimiter=" ")
                for row in reader:
                    if row[1] == "1":
                        bad_list.append(storage.path(row[0]))
                    elif row[2] == "1":
                        empty_list.append(storage.path(row[1]))
                    elif row[3] == "1":
                        good_list.append(storage.path(row[2]))

            return JsonResponse(
                {"success": "true", "empty": empty_list, "animal": good_list,
                 "broken": bad_list})
        else:
            return JsonResponse({"success": "false", "message": "плохо"},
                                status=403)

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'me ssage': 'unsupported method'}, status=403)
