from datetime import datetime, timezone

import yaml

APP_VERSION = "2.11.0"  # before this changes

APP_VERSION_DETAILS = {}
with open("config/versions.yaml", "r") as f:
    APP_VERSION_DETAILS = yaml.safe_load(f.read())

APP_COMMIT_BRANCH = APP_VERSION_DETAILS.get("APP_COMMIT_BRANCH", "dev")
APP_COMMIT_HASH = APP_VERSION_DETAILS.get("APP_COMMIT_HASH", "-")
APP_COMMIT_TIME = APP_VERSION_DETAILS.get("APP_COMMIT_TIME", "-")
APP_BUILD_TIME = APP_VERSION_DETAILS.get(
    "APP_BUILD_TIME", datetime.now(timezone.utc).isoformat()
)
APP_BUILD_NUMBER = APP_VERSION_DETAILS.get("APP_BUILD_NUMBER", "-1")

APP_VERSION_DICT = {
    "VERSION": APP_VERSION,
    "BRANCH": APP_COMMIT_BRANCH,
    "COMMIT": APP_COMMIT_HASH,
    "COMMIT TIME": APP_COMMIT_TIME,
    "BUILD TIME": APP_BUILD_TIME,
    "BUILD NUMBER": APP_BUILD_NUMBER,
}
