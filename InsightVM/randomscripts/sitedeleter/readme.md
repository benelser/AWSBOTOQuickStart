# Simple Script to Delete Stale Sites
This python script can be used to delete a bunch of old crusty sites from your nexpose/IVM console.

## Assumptions
- CSV is inside the same dir as script when ran
- CSV has no header row
- CSV only has one row equal to the site name as it is defined inside the console

## How
Builds a python dictionary that is used for site name look up comparison. If a match is found a DELETE call is then made to the [API](https://help.rapid7.com/insightvm/en-us/api/index.html#operation/deleteSite).
