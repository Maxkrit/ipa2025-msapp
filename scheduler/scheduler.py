import time
import json
from bson import json_util
from database import get_router_info
from producer import produce

INTERVAL = 10.0


def scheduler():
    print("Scheduler is starting...")
    while True:
        start_time = time.time()
        print(f"[{time.ctime(start_time)}] Scheduler running job...")

        try:
            router_list = get_router_info()
            if not router_list:
                print("  - No routers found in database.")
            else:
                print(f"  - Found {len(router_list)} routers. Sending jobs...")
                for router in router_list:
                    message_body = json.dumps(router, default=json_util.default)
                    produce(message_body)
                    print(f"    - Sent job for router: {router.get('ip', 'N/A')}")

        except Exception as e:
            print(f"An error occurred in scheduler loop: {e}")

        time_to_wait = INTERVAL - (time.time() - start_time)
        if time_to_wait > 0:
            time.sleep(time_to_wait)


if __name__ == "__main__":
    scheduler()
