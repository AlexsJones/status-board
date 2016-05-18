# status-board
A quick python based status board for endpoints based on [Miracle-board](https://github.com/xhacker/miracle-board)

It's customised a bit more for my liking and lets you see response times.


## Quick start
```
pip install -r requirements.txt
pip install gunicorn //if you are on windows use a different container for running your flask site like twisted.
```
Edit the config file to point to the sites you care about
```
gunicorn -w 4 -b INTERFACE:5000 run:app --daemon
```
<img src="screenshot1.png" width="698">
