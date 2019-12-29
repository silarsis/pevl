from __future__ import print_function
import json
import event


upgrader = event.Upgrader()


def ingest_log(ev):
    upgraded = upgrader.ingest(ev['Sns']['Message'])
    print(upgraded)
    return upgraded


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    return [ ingest_log(e) for e in event['Records'] ]