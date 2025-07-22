# data_engineer_assessment

docker compose -f docker-compose.initial.yml up --build -d

1. Run `bash script.sh`
    To create and activate vertuval env in python
    compose docker file and up the container 
    create env variable 
    run intial scripts for creatiin table etc..

2. Run `bash script_job.sh` 
    This will call the ETL jobs


3. coonect to docker shell
    mysql -u root -p 
    6equj5_root

4. verify tables after creation 
    SELECT * FROM information_schema.tables WHERE table_schema = 'home_db';

5.  validate data 
    select * from home_db.HOA; 



# to external clints
# driver properties 
allowPublicKeyRetrieval = true
useSSL = false


docker cp mysql-container:/var/lib/mysql/ca.pem ./ssl/ca.pem
docker cp mysql-container:/var/lib/mysql/client-cert.pem ./ssl/client-cert.pem
docker cp mysql-container:/var/lib/mysql/client-key.pem ./ssl/client-key.pem
docker cp mysql-container:/var/lib/mysql/client-key.pem ./ssl/client-key.pem
docker cp mysql-container:/var/lib/mysql/client-cert.pem ./ssl/client-cert.pem
docker cp mysql-container:/var/lib/mysql/ca.pem ./ssl/ca.pem
