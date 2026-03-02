import time
import httpx


class FirefliesError(Exception):
    pass


class FirefliesClient:
    def __init__(self, api_key: str, timeout_seconds: int = 20) -> None:
        self.api_key = api_key
        self.endpoint = "https://api.fireflies.ai/graphql"
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def parse_transcript_id(link: str) -> str | None:
        if not link:
            return None
        from urllib.parse import urlparse

        try:
            parsed = urlparse(link)
        except Exception:
            return None
        if not parsed.path:
            return None
        parts = [part for part in parsed.path.split("/") if part]
        if not parts:
            return None
        last = parts[-1]
        if "::" in last:
            return last.split("::")[-1]
        return last

    def _post(self, query: str, variables: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"query": query, "variables": variables or {}}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.endpoint, json=payload, headers=headers)
        if response.status_code >= 400:
            raise FirefliesError(f"HTTP {response.status_code}: {response.text}")
        data = response.json()
        if data.get("errors"):
            raise FirefliesError(str(data["errors"]))
        return data.get("data", {})

    def validate_key(self) -> bool:
        query = "query { user { email } }"
        try:
            data = self._post(query)
        except FirefliesError:
            return False
        return bool(data.get("user", {}).get("email"))

    def get_transcript(self, transcript_id: str) -> dict:
        query = """
        query Transcript($id: String!) {
          transcript(id: $id) {
            id
            title
            date
            duration
            meeting_link
            sentences {
              index
              speaker_name
              speaker_id
              text
              start_time
              end_time
            }
          }
        }
        """
        data = self._post(query, {"id": transcript_id})
        transcript = data.get("transcript")
        if not transcript:
            raise FirefliesError("Transcript not found")
        return transcript

    def poll_transcript(
        self,
        transcript_id: str,
        attempts: int = 5,
        delay_seconds: int = 10,
    ) -> dict:
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                return self.get_transcript(transcript_id)
            except Exception as exc:
                last_error = exc
                time.sleep(delay_seconds)
        raise FirefliesError(f"Transcript polling failed: {last_error}")
