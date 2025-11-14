import requests

COUNT_PER_REQUEST = 1000

def login(ems_hostname: str, ems_port: int, username: str, password: str, site: str="") -> requests.Session:
    session = requests.Session()
    login_url = f"https://{ems_hostname}:{ems_port}/api/v1/auth/signin"

    payload = {"name": username, "password": password}
    if site:
        payload["site"] = site

    response = session.post(login_url, headers={"Ems-Call-Type": "2"},data=payload, verify=False)
    csrf_token = response.cookies.get("csrftoken")
    session.headers.update({"X-CSRF-Token": csrf_token})
    return session


def make_ems_post(hostname: str, port: int, endpoint: str, session: requests.Session, payload: dict) -> dict:
    response = session.post(f"https://{hostname}:{str(port)}/{endpoint}", headers={"Ems-Call-Type": "2", "Referer": hostname}, json=payload, verify=False)
    response.raise_for_status()
    return response.json()


def get_ems_inventory(hostname: str, port: int, session: requests.Session, site: str="") -> dict:
    endpoint = "api/v1/endpoints/index"
    payload = {
        "order_by": "name",
        "count": str(COUNT_PER_REQUEST)
    }
    return make_ems_post(hostname, port, endpoint, session, payload)

