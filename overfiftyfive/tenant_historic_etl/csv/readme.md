# Tenant Historic ETL Notes
The following code is an example of how to submit the production data files.

rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress /Users/bmika/Developer/over55/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv/prod_employee.csv django@192.168.0.1:/home/django/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv;

rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress /Users/bmika/Developer/over55/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv/prod_employer.csv django@192.168.0.1:/home/django/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv;

rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress /Users/bmika/Developer/over55/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv/prod_orders.csv django@192.168.0.1:/home/django/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv;

rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress /Users/bmika/Developer/over55/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv/prod_small_job_employers.csv django@192.168.0.1:/home/django/overfiftyfive-django/overfiftyfive/tenant_historic_etl/csv;

As an aside, please [read these articles](https://www.digitalocean.com/community/tutorials/how-to-copy-files-with-rsync-over-ssh).
