import json
import event


@event.upgrade('v0.1')
def split_first_last_name(event):
    event['first'], event['last'] = event['name'].split()

@event.upgrade('v0.2')
def add_dob(event):
    event['dob'] = None  # Don't have this, new data wasn't collected for earlier versions


# This should have a list of upgrades
upgrader = event.Upgrader(upgrades=[split_first_last_name, add_dob])


def ingest_log(ev):
    upgraded = upgrader.ingest(ev['Sns']['Message'])
    print(upgraded)
    return upgraded


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    return [ ingest_log(e) for e in event['Records'] ]