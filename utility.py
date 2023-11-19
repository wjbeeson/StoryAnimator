from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from word import Word

credentials = ServiceAccountCredentials.from_stream("keys/google.json")
client = storage.Client(credentials=credentials, project='Reddit Stories')
bucket = client.get_bucket('narration_files')


def upload_file_to_google(filename):
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    return blob.public_url


def download_file_from_google():
    pass


# this method is just a software engineering solution to use old code
def get_sync_values_from_timestamps(timestamps):
    sync_values = []
    for word in timestamps:
        word: Word
        duration = word.end_time - word.start_time
        sync_values.append((word.start_time, duration))
    return sync_values
