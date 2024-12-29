# Domains
- this steps assume we already have access to a domain we can manage
- we have one main domain for the app frontend
- the backend service is on a subdomain
## creating-subdomains
- on the domain, click manage domain
    - for the subdomain just give it a name i.e api
        - on DNS /name servers
            - create a new entry
                - TYPE : `A`
                - Name : i.e `api`
                - Points to : ` VPS IP ADDRESS` for example `195.28.0.22`
                - TTL : leave the default value
                - now the full subdomain will be `api.main-domain.com`
                
    - at the end you should be able to visit the subdomain `api.main-domain.com`