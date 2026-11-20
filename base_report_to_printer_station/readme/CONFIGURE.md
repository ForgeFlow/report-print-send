1. Go to *Settings > Technical > Printing > Print Stations* and create a station for each
   printer. A printer belongs to one station only.
2. Set the printing action "Use the computer's print station" on the reports that must
   print by station. To set it on users instead, set those reports to "Use user's
   defaults": by default every report sends to the client, which overrides the user's
   action.

Each station is linked to one computer. The first user who prints from a computer
without a station chooses it from the list of stations; a station already linked to
another computer is shown as in use and cannot be chosen. A Print Manager can also link
a computer from the station form with *Register this computer*, which unlinks the
computer the station had.

The link is stored in the browser. It survives logouts and changes of user, IP address
or network, and it is renewed on every print. It is lost when the browser's cookies are
deleted: if a browser policy deletes cookies on exit, exempt the Odoo domain.
