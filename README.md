# data_engineer_assessment




docker compose -f docker-compose.initial.yml up --build -d




mysql -u root


# driver properties 
allowPublicKeyRetrieval = true
useSSL = false


docker cp mysql-container:/var/lib/mysql/ca.pem ./ssl/ca.pem
docker cp mysql-container:/var/lib/mysql/client-cert.pem ./ssl/client-cert.pem
docker cp mysql-container:/var/lib/mysql/client-key.pem ./ssl/client-key.pem
docker cp mysql-container:/var/lib/mysql/client-key.pem ./ssl/client-key.pem
docker cp mysql-container:/var/lib/mysql/client-cert.pem ./ssl/client-cert.pem
docker cp mysql-container:/var/lib/mysql/ca.pem ./ssl/ca.pem