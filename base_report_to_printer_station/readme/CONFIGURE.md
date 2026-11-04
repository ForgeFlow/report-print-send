1. Go to *Settings > Technical > Printing > Print Stations* and create a station for each
   printer. A printer belongs to one station only.
2. Set the printing action "Use the computer's print station" on the reports that must
   print by station. To set it on users instead, set those reports to "Use user's
   defaults": by default every report sends to the client, which overrides the user's
   action.
3. On each computer, log in as a Print Manager, open the station and click *Register this
   computer*. Several computers, or several browser profiles of one computer, can be
   registered for the same station.

The registration is stored in the browser. It survives logouts and changes of user, IP
address or network, and it is renewed on every print. It is lost when the browser's
cookies are deleted: if a browser policy deletes cookies on exit, exempt the Odoo domain.
