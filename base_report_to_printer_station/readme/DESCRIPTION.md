Send reports to the printer of the computer they are printed from, whoever is logged in.

A print station links one printer to one computer. The first time someone prints from a
computer, Odoo asks for the station of that computer, among the stations no other
computer uses. Odoo stores a random token in a cookie of that browser and keeps only its
hash. When a report uses the action "Use the computer's print station", Odoo reads the
cookie and sends the report to the station's printer. Nothing is ever sent to the
printer of another station.

The station of the current computer is shown in the top bar.
