# Panmen Tool Recap Export

## curl

### auth

```
curl -H 'Authorization: Bearer TOKEN' https://api.example.com
```

## nmap

### basic

```
nmap -sV target.com    # Service version detection
```

### stealth

```
nmap -sS -f -D decoy target.com  # Stealth SYN scan
```

## wireshark

### filters

```
tcp.port==443  # HTTPS traffic
---
dns  # DNS queries
```

