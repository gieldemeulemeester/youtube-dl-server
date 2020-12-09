import os, json, youtube_dl, webloc
from collections import ChainMap
from concurrent.futures import ThreadPoolExecutor
from model import Job

class DownloadClient:
    def __init__(self):
        self.jobs = []
        self.download_executor = ThreadPoolExecutor(max_workers=2)
        self.app_defaults = {
            "YDL_FORMAT": "bestvideo+bestaudio/best",
            'YDL_EXTRACT_AUDIO_FORMAT': None,
            'YDL_EXTRACT_AUDIO_QUALITY': '192',
            'YDL_RECODE_VIDEO_FORMAT': None,
            'YDL_OUTPUT_TEMPLATE': '/youtube-dl/downloads/%(title).200s [%(id)s].%(ext)s',
            'YDL_ARCHIVE_FILE': None
        }
    
    def download_url(self, url: str, request_options: dict, callback: callable = None) -> None:
        with youtube_dl.YoutubeDL(self.get_ydl_options(request_options)) as ydl:
            future = self.download_executor.submit(ydl.download, [url])
            self.jobs.append(Job.Job(url, None, request_options, future, callback))

    def download_webloc(self, filepath: str, request_options: dict, callback: callable = None) -> None:
        with youtube_dl.YoutubeDL(self.get_ydl_options(request_options)) as ydl:
            url = webloc.read(filepath)
            future = self.download_executor.submit(ydl.download, [url])
            self.jobs.append(Job.Job(url, filepath, request_options, future, callback))          

    def get_job(self, id: str) -> Job:
        for job in self.jobs:
            if job.id == id: return job

    def get_job_status(self, id: str) -> str:
        job = self.get_job(id)
        if job == None: return None
        return job.get_status()

    def cancel_job(self, id: str) -> bool:
        job = self.get_job(id)
        if job == None: return False
        return job.cancel()

    def clear_jobs(self) -> None:
        self.jobs = [x for x in self.jobs if x.is_active()]

    def get_ydl_options(self, request_options: dict) -> json:
        request_vars = {
            'YDL_EXTRACT_AUDIO_FORMAT': None,
            'YDL_RECODE_VIDEO_FORMAT': None,
        }

        requested_format = request_options.get('format', 'bestvideo')

        if requested_format in ['aac', 'flac', 'mp3', 'm4a', 'opus', 'vorbis', 'wav']:
            request_vars['YDL_EXTRACT_AUDIO_FORMAT'] = requested_format
        elif requested_format == 'bestaudio':
            request_vars['YDL_EXTRACT_AUDIO_FORMAT'] = 'best'
        elif requested_format in ['mp4', 'flv', 'webm', 'ogg', 'mkv', 'avi']:
            request_vars['YDL_RECODE_VIDEO_FORMAT'] = requested_format

        ydl_vars = ChainMap(request_vars, os.environ, self.app_defaults)

        postprocessors = []

        if(ydl_vars['YDL_EXTRACT_AUDIO_FORMAT']):
            postprocessors.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ydl_vars['YDL_EXTRACT_AUDIO_FORMAT'],
                'preferredquality': ydl_vars['YDL_EXTRACT_AUDIO_QUALITY'],
            })

        if(ydl_vars['YDL_RECODE_VIDEO_FORMAT']):
            postprocessors.append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': ydl_vars['YDL_RECODE_VIDEO_FORMAT'],
            })

        return {
            'format': ydl_vars['YDL_FORMAT'],
            'postprocessors': postprocessors,
            'outtmpl': ydl_vars['YDL_OUTPUT_TEMPLATE'],
            'download_archive': ydl_vars['YDL_ARCHIVE_FILE']
        }
