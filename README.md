Rolling Reboots on Google Compute Engine (Google Cloud)
========

After being frustrated with rolling updates on GCE, I've written this basic python script that reboots all instances from one Instance Group one at a time, and waits for it to respond to a HTTP Request with a 200 response and then reboots the next instance.
