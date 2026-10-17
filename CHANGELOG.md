## next release

- ADDED profile - DCS game statistics of the pilot, from DCSServerBot (#181)
- ADDED servers - link to the Foothold SITAC of a server, configured in admin (#182)
- FIXED calendar - cadets could not register to events open to cadets and members (#199)
- FIXED calendar - copying an event dropped its image (#190)
- FIXED auth - login failed with a server error when the stored password was not a bcrypt hash (#183)
- FIXED system - frontend container always reported unhealthy (healthcheck reached localhost over IPv6)
- ADDED system - send an API key to DCSServerBot (`API_DCSSERVERBOT_KEY`)
- ADDED system - per-IP rate limit on sign-up and password reset (nginx)
- CHANGED recruitment - history and events restricted to members, admin-only event types reserved to admins
- CHANGED system - image conversion on upload no longer blocks the server
- FIXED calendar - a deleted event is no longer served by its detail page
- FIXED files - an unreadable or oversized image upload is rejected with a clear error
- REMOVED system - reCAPTCHA setting, which was never checked


## 2.2.0

- ADDED calendar - display the terrain header image on events without a custom image
- ADDED admin - manage DCS players UCID
- CHANGED calendar - event badge now refreshes on its own (30s tick), closing votes on time
- FIXED calendar - time remaining before event start rounded up to whole days ("dans 1j" for an event 1 hour away), now shown as days, hours or minutes


## 2.1.1

- FIXED system - HTML and JS frontend caches causing failures
- FIXED system - cleanup old docker images on registry

## 2.1.0

- ADDED roster - BMS section (available also from Landing page)
- ADDED roster - display module popularity (progress bar) for each module
- ADDED calendar - planning view (default for mobile)
- ADDED calendar - open graphs metadata (thumbs & message when copy&paste link into discord)
- ADDED favicon
- ADDED login/logout notifications
- ADDED licence about code and content
- ADDED admin - track files sizes
- CHANGED system - optimize docker image size
- FIXED roster - modules count
- FIXED system - customer deploy stack name
