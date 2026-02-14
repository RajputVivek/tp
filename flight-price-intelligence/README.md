# Deployment Guidelines
On the DigitalOcean server:

cd /root/tp/flight-price-intelligence
git pull


# Restart services:

systemctl restart flightintel
systemctl restart flightintel-bot

# VERY IMPORTANT: Do These 3 Sanity Checks Once
1️⃣ Verify both services are running

# (On the server)

systemctl status flightintel
systemctl status flightintel-bot


# Both should be:

Active: active (running)

# Check logs once (just awareness)
journalctl -u flightintel --since "1 hour ago"
journalctl -u flightintel-bot --since "1 hour ago"


No crashes = you’re golden.