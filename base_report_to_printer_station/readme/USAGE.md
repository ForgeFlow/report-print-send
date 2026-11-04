Print as usual. The report goes to the printer of the station shown in the top bar.

To remove a computer, open its station and click *Revoke* on its line. To move a computer
to another station, register it again from the new station: the old registration is
revoked.

Code that prints without a browser, such as a queued job, passes the station in the
context key `printing_station_id`. The context key is ignored during an HTTP request, so
a client cannot choose a station other than the one its cookie belongs to.
