import os
import time
import logging
import requests
import yt_dlp
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("video-indexer")


class VideoIndexerService:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME")

        self.credential = DefaultAzureCredential()

        self._cached_vi_token = None
        self._token_expiry_time = 0  # epoch timestamp


    # ==========================================================
    #  TOKEN MANAGEMENT
    # ==========================================================

    def _get_arm_token(self):
        try:
            token = self.credential.get_token(
                "https://management.azure.com/.default"
            )
            return token.token
        except Exception as e:
            logger.error(f"Failed to get ARM token: {e}")
            raise


    def _generate_vi_account_token(self):
        arm_token = self._get_arm_token()

        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )

        headers = {"Authorization": f"Bearer {arm_token}"}
        payload = {"permissionType": "Contributor", "scope": "Account"}

        for attempt in range(3):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    token = response.json().get("accessToken")

                    # Cache token for 50 minutes
                    self._cached_vi_token = token
                    self._token_expiry_time = time.time() + (50 * 60)

                    return token

                else:
                    logger.error(
                        f"VI Token Error {response.status_code}: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                logger.warning(f"Retry {attempt+1}/3: {e}")
                time.sleep(2 ** attempt)

        raise Exception("Failed to generate Video Indexer account token.")


    def _get_vi_token(self):
        # If cached and valid → reuse
        if (
            self._cached_vi_token
            and time.time() < self._token_expiry_time
        ):
            return self._cached_vi_token

        return self._generate_vi_account_token()


    # ==========================================================
    #  YOUTUBE DOWNLOAD
    # ==========================================================

    def download_youtube_video(self, url, output_path="temp_video.mp4"):
        logger.info(f"Downloading YouTube video: {url}")

        ydl_opts = {
            "format": "best",
            "outtmpl": output_path,
            "quiet": False,
            "no_warnings": False,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            logger.info("Download complete.")
            return output_path

        except Exception as e:
            raise Exception(f"YouTube download failed: {str(e)}")


    # ==========================================================
    #  UPLOAD VIDEO
    # ==========================================================

    def upload_video(self, video_path, video_name):
        vi_token = self._get_vi_token()

        api_url = (
            f"https://api.videoindexer.ai/{self.location}"
            f"/Accounts/{self.account_id}/Videos"
        )

        params = {
            "accessToken": vi_token,
            "name": video_name,
            "privacy": "Private",
            "indexingPreset": "Default"
        }

        logger.info(f"Uploading {video_path} to Video Indexer...")

        with open(video_path, "rb") as video_file:
            files = {"file": video_file}

            response = requests.post(
                api_url,
                params=params,
                files=files,
                timeout=120
            )

        if response.status_code != 200:
            raise Exception(
                f"Upload failed {response.status_code}: {response.text}"
            )

        video_id = response.json().get("id")
        logger.info(f"Upload successful. Video ID: {video_id}")
        return video_id


    # ==========================================================
    #  POLLING
    # ==========================================================

    def wait_for_processing(self, video_id):
        logger.info(f"Waiting for video {video_id} to process...")

        vi_token = self._get_vi_token()

        headers = {"Authorization": f"Bearer {vi_token}"}

        status_url = (
            f"https://api.videoindexer.ai/{self.location}"
            f"/Accounts/{self.account_id}/Videos/{video_id}/Index"
        )

        while True:
            response = requests.get(
                status_url,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(
                    f"Polling failed {response.status_code}: {response.text}"
                )

            data = response.json()
            state = data.get("state")

            logger.info(f"Current state: {state}")

            if state == "Processed":
                return data
            elif state == "Failed":
                raise Exception("Video indexing failed.")
            elif state == "Quarantined":
                raise Exception("Video quarantined.")

            time.sleep(30)


    # ==========================================================
    #  DATA EXTRACTION
    # ==========================================================

    def extract_data(self, vi_json):
        transcript_lines = []
        ocr_lines = []

        for v in vi_json.get("videos", []):
            insights = v.get("insights", {})

            for t in insights.get("transcript", []):
                transcript_lines.append(t.get("text"))

            for o in insights.get("ocr", []):
                ocr_lines.append(o.get("text"))

        return {
            "transcript": " ".join(transcript_lines),
            "ocr_text": ocr_lines,
            "video_metadata": {
                "duration": vi_json.get("summarizedInsights", {})
                .get("duration", {})
                .get("seconds"),
                "platform": "youtube"
            }
        }