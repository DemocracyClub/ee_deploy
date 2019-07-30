# Every Election build and deploy

## Setup

* `pipenv install`
* `ansible-galaxy install -r requirements.yml`
* Ensure your AWS credentials are in `~/.aws/credentials`
* create `.vault_pass.txt` with your vault password

## Build

* `AWS_PROFILE=everyelection ./packer`

## Deploy

* If we're deploying to production, `export ENVIRONMENT=prod`. Obviously don't do this for a staging deploy!
* `AWS_PROFILE=everyelection ansible-playbook aws.yml -e replace_all=True`

## Databases

DB Migrations are not managed. If there are DB migrations to apply, we must do it manually.

We can optionally scale the back-end out over up to 4 read replicas. Load balancing is handled using a private DNS zone with weighted routing. When we only want to run one database server, we can set up a single CNAME pointing the private DNS zone to the primary read/write server. If we want to add more capacity, we can add more CNAMEs for additional read-replicas (we can also completely remove the primary instance or decrease its weight).

Key points:
* Set the TTL=0 when creating CNAMEs. If we leave it on TTL=300, we'll hammer one server for 5 mins then hammer another one for 5 mins etc
* To balance load evenly across replicas, set the weight of every CNAME to zero (if one is set to not-zero, that one will take all the load)
* When adding a replica, bring up a replica in RDS first then add the CNAME in Route53 once its online
* When removing a replica, remove the CNAME in Route53 first then delete the replica in RDS
