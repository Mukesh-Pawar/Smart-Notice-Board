import requests
from config import API_URL, API_TOKEN, POLL_INTERVAL
from virtual_p10 import VirtualP10


class VirtualESP32:
    def __init__(self, display):
        self.display = display
        self.last_notice_key = None

    def headers(self):
        headers = {
            "Accept": "application/json"
        }

        # Django REST Framework TokenAuthentication
        if API_TOKEN.strip():
            headers["Authorization"] = f"Token {API_TOKEN.strip()}"

        return headers

    def fetch(self):
        try:
            response = requests.get(
                API_URL,
                headers=self.headers(),
                timeout=8
            )

            print(f"[API] HTTP {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    return None, "Invalid JSON"

                # Expected:
                # {"success": True, "notice": {...}}
                notice = data.get("notice") if isinstance(data, dict) else None

                if notice is None:
                    return None, "No active notice"

                if not isinstance(notice, dict):
                    return None, "Unexpected notice format"

                return notice, None

            if response.status_code == 204:
                return None, "No active notice"

            if response.status_code == 401:
                return None, "Unauthorized - check API_TOKEN"

            if response.status_code == 403:
                return None, "Forbidden - check user/device permission"

            if response.status_code == 404:
                return None, "API endpoint not found"

            return None, f"HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            return None, "Cannot connect to Django"

        except requests.exceptions.Timeout:
            return None, "API request timeout"

        except requests.exceptions.RequestException as exc:
            return None, f"Request error: {exc}"

    def check_once(self):
        notice, error = self.fetch()

        if error:
            print("[ESP32]", error)
            self.display.set_status(error)

            if error == "No active notice":
                self.display.clear_notice()

            return

        notice_id = notice.get("id")
        title = str(notice.get("title", "SMART NOTICE BOARD"))
        message = str(notice.get("message", ""))
        priority = str(notice.get("priority", ""))

        # Avoid refreshing the P10 when the same notice is received.
        notice_key = notice_id
        if notice_key is None:
            notice_key = f"{title}|{message}|{priority}"

        if notice_key != self.last_notice_key:
            print()
            print("========== NEW NOTICE ==========")
            print("ID       :", notice_id)
            print("Title    :", title)
            print("Message  :", message)
            print("Priority :", priority)
            print("================================")
            print()

            self.display.show_notice(title, message, priority)

            self.last_notice_key = notice_key
            self.display.set_status(
                f"Display updated | Notice ID: {notice_id}"
            )
        else:
            self.display.set_status(
                f"Connected | Notice ID: {notice_id} | No change"
            )

    def schedule(self):
        self.check_once()
        self.display.root.after(
            POLL_INTERVAL * 1000,
            self.schedule
        )

    def run(self):
        print("========================================")
        print("       VIRTUAL ESP32 STARTED")
        print("========================================")
        print("API      :", API_URL)
        print("Interval :", POLL_INTERVAL, "seconds")
        print("----------------------------------------")

        self.schedule()
        self.display.root.mainloop()


def main():
    display = VirtualP10()
    VirtualESP32(display).run()


if __name__ == "__main__":
    main()
