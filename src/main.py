import asyncio
import datetime
import threading
import time

import requests

from thilde_event import ThildeEvent
from thilde_requests import RequestFactory, Credentials
from utils import fetch_event_id_from_url, wait_until_dt

# r = requests.get('https://api.github.com/events')
# print(r)

"""
1. get event info
2. validate login details
3. ping server to find start offset

4. wait untill t- offset+5
5. reloggin to update keys
6. at t - offset*2 start polling 20x/second elns
8. when success response stop 

"""

class Poller:
    def __init__(self, request_factory: RequestFactory, event: ThildeEvent):
        self.request_factory = request_factory
        self.event = event
        self.stop = False
        self.counter = 0



    def _p(self):
        id = self.counter
        self.counter += 1

        thread_time_delta = self.event.get_timedelta_to_reg_start()
        time_delta = thread_time_delta.seconds + thread_time_delta.microseconds / 1e6

        print("request {} started at {:.2f} ".format(id, time_delta))
        response = self.request_factory.send_registration_request(self.event)
        if not self.stop:
            if response.status_code == 201:
                # 201 created -> success
                print("\n\nHit !")
                print("request {:<3} started at T-{:.2f} successfully registered to event {}".format(id, time_delta, self.event.id))
                print("starting cleanup")
                self.stop = True
            elif response.status_code == 409:
                # 409 conflict -> already created pbl
                self.stop = True
                print("request {:<3} overshoot, you shold never see this".format(id))
                pass
            elif response.status_code == 400:
                # 400 bad request -> not opened yet
                print("request {:<3} too early".format(id))
                pass
            else:
                print("request {} statuscode {}".format(id, response.status_code))


    def start_polling(self):
        threads = []
        print(f"starting to poll at T-{self.event.get_timedelta_to_reg_start().total_seconds()}")

        while not self.stop:
            t = threading.Thread(target=self._p)
            t.start()
            threads.append(t)
            time.sleep(0.01)

        for t in threads:
            t.join()





def main():
    amazing_title = "==" + (20 * " ") + f"    Trygves amazing thilde bot    " + (20 * " ") + "=="
    print(len(amazing_title) * "=")
    print(amazing_title)
    print(len(amazing_title) * "=")
    print()
    valid_id = False
    while not valid_id:
        event_id = input('input event id: ').rstrip("\n")

        if "tihlde.org" in event_id:
            event_id = fetch_event_id_from_url(event_id)

        if event_id.isdigit():
            try:
                event = ThildeEvent(int(event_id))
                valid_id = True
            except Exception:
                print(f"error fetching event with id {event_id}")
        else:
            print(f"invalid id submitted <{event_id}> is not a number")
    event.display_event()


    valid_credentials = False

    while not valid_credentials:
        username = input('input username: ').rstrip("\n")
        password = input('input password: ').rstrip("\n")
        cd = Credentials(username=username, password=password)
        request_factory = RequestFactory(credentials=cd)
        if request_factory.test_credentials():
            print("credential test ok")
            valid_credentials = True
        else:
            print("login error")

    # if event.registration_start < datetime.datetime.now(event.registration_start.tzinfo):
    #     print("Evenet has been open for some time log on manually")
    #     return

    wake_time = event.registration_start - datetime.timedelta(seconds=10)
    wait_until_dt(wake_time, verbose=True)

    print("T-5 sec, refreshing the login token")
    token_refresh_at = event.registration_start - datetime.timedelta(seconds=5)
    wait_until_dt(token_refresh_at, verbose=False)
    request_factory.refresh_token()
    print("refresh ok")

    print("T-1 sec, starting the polling sequence")
    poll_start_at = event.registration_start - datetime.timedelta(seconds=1)
    wait_until_dt(poll_start_at, verbose=False)
    poller = Poller(request_factory=request_factory, event=event)
    poller.start_polling()


if __name__ == '__main__':
    main()








