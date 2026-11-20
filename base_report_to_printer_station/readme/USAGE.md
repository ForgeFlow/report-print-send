Print as usual. The report goes to the printer of the station shown in the top bar. On
a computer with no station yet, click *Choose print station* in the top bar and pick
the station; stations in use on another computer are shown but cannot be chosen.

To free a station, a Print Manager opens it and clicks *Revoke* on its computer line.
To move a computer to another station, register it again from the new station: the old
link is revoked.

Code that prints without a browser, such as a queued job, passes the station in the
context key `printing_station_id`. The context key is ignored during an HTTP request, so
a client cannot choose a station other than the one its cookie belongs to.

Code that needs the station before printing can return
`env["printing.station"]._action_choose(records, method)` when there is none: the user
chooses the station, then the browser calls `method` on `records` again.
