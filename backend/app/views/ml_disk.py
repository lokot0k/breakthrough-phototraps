import csv
import io
import json
import os
import shutil

from PIL import Image
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from googleapiclient.http import MediaIoBaseDownload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from oauth2client.client import GoogleCredentials

from app.models.ml_model import generate_submission_folder, model
from app.utils.drive_downloader import download_files, createRemoteFolder, \
    moveFile
from app.utils.storage import MyStorage
from djangoProject import settings


class MlDiskView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        pass

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/drive']
        st = MyStorage()
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(settings.STATIC_ROOT / "token.json"):
            creds = Credentials.from_authorized_user_file(
                settings.STATIC_ROOT / "token.json",
                SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.STATIC_ROOT / "client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(settings.STATIC_ROOT / "token.json", 'w') as token:
                token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        folder_id = json.loads(request.body)['folder']  # request.body.folder
        shutil.rmtree(settings.MEDIA_ROOT)
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        d = download_files(service, folder_id, st.path(""))
        directory = os.fsencode(settings.MEDIA_ROOT)
        storage = MyStorage()
        generate_submission_folder([model],
                                   settings.MEDIA_ROOT)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.lower().endswith(".png") or filename.lower().endswith(
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
        animal_id = createRemoteFolder(service, "животные", folder_id)
        broken_id = createRemoteFolder(service, "битые", folder_id)
        empty_id = createRemoteFolder(service, "пустые", folder_id)

        paths = ["a/", "b/", "e/", "ab/", "ae/", "be/", "abe/"]

        for path in paths:
            (settings.MEDIA_ROOT / path).mkdir(parents=True, exist_ok=True)
        with open(storage.path('submission.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if not row or len(row) != 4:
                    continue
                if row[1] == "1":
                    bad_list.append(f"/media/{row[0]}")
                    moveFile(service, d[row[0]], broken_id)
                    for path in paths:
                        if 'b' in path:
                            shutil.copy(storage.path(row[0]), storage.path(path + row[0]))
                elif row[2] == "1":
                    empty_list.append(f"/media/{row[0]}")
                    moveFile(service, d[row[0]], empty_id)
                    for path in paths:
                        if 'e' in path:
                            shutil.copy(storage.path(row[0]), storage.path(path + row[0]))
                elif row[3] == "1":
                    good_list.append(f"/media/{row[0]}")
                    moveFile(service, d[row[0]], animal_id)
                    for path in paths:
                        if 'a' in path:
                            shutil.copy(storage.path(row[0]), storage.path(path + row[0]))

        for path in paths:
            shutil.make_archive(storage.path(path), "zip", storage.path(path))

        return JsonResponse(
            {"empty": empty_list, "animal": good_list,
             "broken": bad_list})

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'me ssage': 'unsupported method'}, status=403)
