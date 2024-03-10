# Integration: ApiLogicServer + Keycloak

This repo contains a demo for apilogicserver integration with keycloak oidc JWT authentication.  It is an attempt to integrate this more natively into API Logic Server.

Status - 3/7:

1. able to access keycloak for login using modified sra at localhost.
2. not able to obtain jwt data for roles/authorization

&nbsp;

## Run:
```
cd devops/keycloak
docker-compose up
```

This will run keycloak on the docker host (use admin, password):
- keycloak (http://localhost:8080) 

&nbsp;

### Define Users and Roles

This works - you can define users, and they are available (with their roles) at runtime (see the jwt.io screenshot, below):

![Users](images/kc-users.png)

### Define Attributes

I can enter User Attributes:

![Users](images/kc-attrs.png)

And, [using this](https://www.baeldung.com/keycloak-custom-user-attributes), register mappers:

![kc-client-attr-mapper](images/kc-client-attr-mapper.png)

You must provide the `Token Claim Name`:

![kc-client-attr-mapper-def](images/kc-client-attr-mapper-def.png)

### Authorization Failing

Login as u1.   Somehow, the `customer` role is assigned, which makes it fail (return >1 Category).

&nbsp;

## Test:

### 1. Keycloak Unit Test

Verify keycloak login with demo, demo

```bash
# keycloak realm named "kcals"
KC_BASE=http://localhost:8080/realms/kcals

echo "\n\noidc token endpoint"
TOKEN_ENDPOINT=$(curl ${KC_BASE}/.well-known/openid-configuration | jq -r .token_endpoint)
echo "TOKEN_ENDPOINT: ${TOKEN_ENDPOINT} \n"

echo "retrieve an access token by logging in "
TOKEN=$(curl ${TOKEN_ENDPOINT} -d 'grant_type=password&client_id=alsclient' -d 'username=u1' -d 'password=p' | jq -r .access_token)
echo "TOKEN: ${TOKEN} \n"

# test the authentication
curl http://localhost:5656/api/Category -H "Authorization: Bearer ${TOKEN}" | jq .

```

### 2. Start APP Logic Server

Use first Run Config.

* If possible, I'd like to simplify setup, and make debugging easier, so trying to run the app natively.

&nbsp;

## Adapted Implementation

Several changes to adapt the original poc to API Logic Server structure:

1. Updated `security/system/authentication.py` 
    * Call a new `configure_auth` function in the Keycloak Provider
    * Pass jwt_data to `get_user(identity, jwt_data)` (arg 2, instead of password)
    * This removes dependency on this file to provider type.
2. Introduced `security/authentication_provider/keycloak/auth_provider`
    * Moved the settings and `get_jwt_public_key` to there
    * This centralizes all the keycloak elements into its provider
    * There is a `config/config.py` setting to activate the Keycloak Provider.
        * This will later be a CLI command.
3. Added the docker compose material (including imports) to the `devops` dir
4. Note **interim SRA** is included in `ui/safrs-react-admin`
5. To login, see the `Auth` object in the admin app: demo, demo


![Attempt](images/integrate-keycloak.png)

### Inspecting Access Tokens

You can use jwt.io:

![jwt.io](images/jwt.io.png)


## Initial Implementation (for reference)

- the `$PWD/projects` was mounted at `/projects` in the ApiLogicServer container
- A project named [`KCALS`](projects/KCALS) was created (default nw, with authentication):

```bash
mkdir projects
chmod 777 projects # we need to be able to write to this directory from the container
docker run  $PWD/projects:/projects -it apilogicserver/api_logic_server bash -c "ApiLogicServer create --project_name=/projects/KCALS --db_url= ; ApiLogicServer add-auth --project_name=/projects/KCALS"
```

For users to be able to authenticate with JWTs signed by keycloak, we have to download the JWK signing key from keycloak and use that to validate the JWTs. 
JWT validation is implemented in [projects/KCALS/security/system/authentication.py](projects/KCALS/security/system/authentication.py). 

By default, apilogicserver authentication uses a user database. Our users are defined in keycloak however. I had to change [auth_provider.py](auth_provider.py) for this to (kinda) work.

&nbsp;

## React-Admin

Nginx is used to host the safrs-react-admin frontend at http://localhost/admin-app .

&nbsp;

## Persisting Keycloak Data

keycloak data is stored inside the keycloak container in /opt/keycloak/data .
To make this persistent, you should mount this volume. Currently, only the "import" folder is mounted.
This import folder contains json files exported by me. These json files are imported when the container starts with the " --import-realm" command line switch ( https://www.keycloak.org/server/importExport )

You can try this:

```bash
$ mkdir data
$ mv import data # the import folder containing the json files
$ chmod 777 data # make sure the container keycloak user can write to this folder
```

Then, change the docker-compose keycloak volumes to:

    volumes:
        - $PWD/data:/opt/keycloak/data

Finally, update the docker-compose file so that the imports don't overwrite the mounted volume settings:
1. Remove the `--import-realm`
2. Remove `- $PWD/import:/opt/keycloak/data/import`
This way, the /opt/keycloak/data will remain on the docker host mounted directory ($PWD/data).

Access data - this does not appear to work (no cli):
```bash
docker cp keycloak:/opt/keycloak/data ~/Desktop/keycloak

```

&nbsp;

## Notes: Accessing the jwt at runtime

To retrieve user info from the jwt, you may want to look into these functions:
https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
as used in security/system/authentication.py

## Saved snippet

Aside - can use this as bearer... jwt.io will decode it

```python
data = {
            "grant_type": "password",
            "client_id": "alsclient",
            "username" :f"{username}",
            "password": f"{password}"
        }
        resp = requests.post(f"{TOKEN_ENDPOINT}", data)
        if resp.status_code == 200:
            resp_data = json.loads(resp.text)
            access_token = resp_data["access_token"]
            return jsonify(access_token=access_token)
```
&nbsp;
