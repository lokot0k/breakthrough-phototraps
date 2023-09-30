import os


def download_files(service, folder_id, output_dir):
    page_token = None
    d = dict()
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']

            if mime_type == 'application/vnd.google-apps.folder':
                # If the file is a subfolder, skip
                pass
            else:
                d[file_name] = file_id
                # If the file is not a folder, download it.
                request = service.files().get_media(fileId=file_id)
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, 'wb+') as f:
                    f.write(request.execute())

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return d


def createRemoteFolder(driver_service, folderName, parentID=None):
    body = {
        'name': folderName,
        'mimeType': "application/vnd.google-apps.folder"
    }
    if parentID:
        body['parents'] = [parentID]
    root_folder = driver_service.files().create(body=body).execute()
    return root_folder['id']


def moveFile(drive_service, file_id, folder_id):
    file = drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        fields='id, parents'
    ).execute()
    return file
