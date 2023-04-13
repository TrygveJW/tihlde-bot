import asyncio
import datetime
import threading
import time

import requests

from thilde_event import ThildeEvent
from thilde_requests import RequestFactory, Credentials
from utils import fetch_event_id_from_url, wait_until_dt



class Poller:
    def __init__(self, request_factory: RequestFactory, event: ThildeEvent):
        self.request_factory = request_factory
        self.event = event
        self.stop = False
        self.counter = 0
        self.to_early_count = 0




    def _p(self):
        id = self.counter
        self.counter += 1

        thread_time_delta = self.event.get_timedelta_to_reg_start()
        time_delta = thread_time_delta.seconds + thread_time_delta.microseconds / 1e6

        # print("request {} started at {:.2f} ".format(id, time_delta))
        response = self.request_factory.send_registration_request(self.event)
        if not self.stop:
            if response.status_code == 201:
                # 201 created -> success
                print("\nHit !")
                print("request {:<3} started at T-{:.2f} successfully registered to event {}".format(id, time_delta, self.event.id))
                print("starting cleanup")
                self.stop = True
            elif response.status_code == 409:
                # 409 conflict -> already created pbl
                self.stop = True
                print("\nrequest {:<3} got already signed up, stopping".format(id))
                pass
            elif response.status_code == 400:
                # 400 bad request -> not opened yet
                # print("request {:<3} too early".format(id))
                self.to_early_count += 1
                pass
            else:
                print("\nrequest {} statuscode {}".format(id, response.status_code))


    def start_polling(self):
        threads = []
        print(f"starting to poll at T-{self.event.get_timedelta_to_reg_start().total_seconds()}")

        while not self.stop:
            t = threading.Thread(target=self._p)
            t.start()
            threads.append(t)

            print("Current request count is: {:>6} of the {:>5} where to early".format(self.counter, self.to_early_count), end="\r")
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
        event_id = input('input event id or url: ').rstrip("\n")

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


    wake_time = event.registration_start - datetime.timedelta(seconds=10)
    wait_until_dt(wake_time, verbose=True)
    print("T-10 sec, refreshing the login token")
    request_factory.refresh_token()
    print("refresh ok")

    poll_start_at = event.registration_start - datetime.timedelta(seconds=1)
    wait_until_dt(poll_start_at, verbose=False)
    print("T-1 sec, starting the polling sequence")
    poller = Poller(request_factory=request_factory, event=event)
    poller.start_polling()


if __name__ == '__main__':
    main()








