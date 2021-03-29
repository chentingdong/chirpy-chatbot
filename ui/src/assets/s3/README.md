This dir holds the sync from s3, for development convenience. Do not need local copy for production.
 
aws s3 bucket:
https://s3.console.aws.amazon.com/s3/buckets/illusionist/?region=us-east-1

sync from s3 to this dir
aws s3 sync s3://illusionist/dev ./dev

sync from local to s3 
aws s3 sync ./dev s3://illusionist/dev
