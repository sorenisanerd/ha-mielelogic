DOMAIN = "mielelogic"

CLIENT_ID = "YV1ZAQ7BTE9IT2ZBZXLJ"
AUTH_URL = "https://sec.mielelogic.com/v3/token"
API_URL_TEMPLATE = "https://api.mielelogic.com/v7/Country/{country}/Laundry/{laundry_id}/laundrystates?language=en"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "da,en-US;q=0.7,en;q=0.3",
    "Origin": "https://mielelogic.com",
    "Referer": "https://mielelogic.com/",
}

UPDATE_INTERVAL_SECONDS = 60

MACHINE_TYPE_WASHER = "washer"
MACHINE_TYPE_DRYER = "dryer"
MACHINE_SYMBOL_WASHER = 0
MACHINE_SYMBOL_DRYER = 1
MACHINE_COLOR_IN_USE = 2

STATE_AVAILABLE = "available"
STATE_NOT_AVAILABLE = "not_available"
