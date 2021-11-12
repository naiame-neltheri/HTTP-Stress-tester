# HTTP Stress tester
HTTP Stress tester written on `python 3` with threading

## HTTP Load tester
This tool is written on python using threads. The tools itself only firest HTTP request for specified URL until the maximum HTTP request is reached. You can define thread numbers with options.
See more on help menu
```
./httpLoader.py -h
usage: httpLoader.py [-h] [-t THREAD] [-H HEADER] [-T TIMEOUT] [-k] max url

HTTP Load tester by Naiame Nel'theri

positional arguments:
  max         Number of requests to send
  url         URL for web service

optional arguments:
  -h, --help  show this help message and exit
  -t THREAD   Thread count, default is 1
  -H HEADER   Custom header, ex: Authorization: Bearer test
  -T TIMEOUT  Set timeout for warning message
  -k          Set SSL verification to false

```
- With thread option you can increase the speed of stress testing
- With header option you can specify custom header for every request made by script

Example output of the script
```
./httpLoader.py -H "Authorization: Bearer dGVzdAo=.dGVzdAo=.dGVzdAo=" -k -t 1000 1000 https://test.test
[+] Total of 1000 requests sent
[+] Average Time : 0.60 second

```

For requesting feature please raise an issue
