#Deployment Guidelines
On the DigitalOcean server:

cd /root/tp/flight-price-intelligence
git pull


Restart services:

systemctl restart flightintel
systemctl restart flightintel-bot