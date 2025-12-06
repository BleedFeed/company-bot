import json
import logging
import time

import requests
from PIL import Image
from requests.models import HTTPError
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich_pixels import Pixels

from hash import lXt_py
from profitCalculator import calculate_optimum_price, calculate_profit


class SatisElemani:
    def __init__(self):
        self.tz_offset = time.timezone / 60
        self.s = requests.Session()
        self.constants = None
        self.owned_resources = None
        self.acceleration_events = None
        self.weather = None
        self.headers = {
            "Host": "www.simcompanies.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-GPC": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Referer": "https://www.simcompanies.com/",
            "Cache-Control": "no-cache",
            "Origin": "https://www.simcompanies.com",
        }
        self.session_cookie_ister_misin_cocuk_adam()
        self.get_csrf()
        self.get_constants()

    def session_cookie_ister_misin_cocuk_adam(self):
        try:
            self.s.get("https://www.simcompanies.com/api/csrf/", headers=self.headers)
        except Exception:
            logging.error("An unexpected error occurred", exc_info=True)

    def get_csrf(self):
        try:
            csrf_response = self.s.get(
                "https://www.simcompanies.com/api/csrf/", headers=self.headers
            )
            self.csrf = csrf_response.json()["csrfToken"]
        except Exception:
            logging.error("An unexpected error occurred", exc_info=True)

    def generate_headers(self, url):
        seconds = int(time.time() * 1000)

        url_without_domain = "/" + "/".join(url.split("/")[3:])
        prot = str(seconds) + url_without_domain
        return (seconds, lXt_py(prot))

    def get_constants(self):
        try:
            core_url = "https://www.simcompanies.com/api/v2/constants/core/"
            resources_url = "https://www.simcompanies.com/api/v2/constants/resources/"
            buildings_url = "https://www.simcompanies.com/api/v2/constants/buildings/"
            core_constants = self.s.get(core_url, headers=self.s.headers)
            time.sleep(0.2)
            resources_constants = self.s.get(resources_url, headers=self.s.headers)
            time.sleep(0.2)
            buildings_constants = self.s.get(buildings_url, headers=self.s.headers)
            time.sleep(0.2)
            if (
                core_constants.status_code == 200
                and resources_constants.status_code == 200
                and buildings_constants.status_code == 200
            ):
                self.constants = {
                    "core": core_constants.json(),
                    "resources": resources_constants.json(),
                    "buildings": buildings_constants.json(),
                }
            else:
                raise HTTPError(
                    f"constantlar çekilemedi response codeları core:{core_constants.status_code} resources:{resources_constants.status_code} buildings:{buildings_constants.status_code}"
                )

        except Exception:
            logging.error("An unexpected error occurred", exc_info=True)

    def get_realm_variables(self):
        try:
            acc_events_url = f"https://www.simcompanies.com/api/v3/encyclopedia/events/{self.realm_id}"
            weather_url = f"https://www.simcompanies.com/api/v2/weather/{self.realm_id}"

            acc_events_response = self.s.get(acc_events_url, headers=self.headers)
            time.sleep(0.2)
            weather_response = self.s.get(weather_url, headers=self.headers)

            acc_events_response.raise_for_status()
            weather_response.raise_for_status()
            self.acceleration_events = acc_events_response.json()["events"]
            self.weather = weather_response.json()

        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_account_data(self):
        url = "https://www.simcompanies.com/api/v3/companies/auth-data/"
        (seconds, prot_hash) = self.generate_headers(url)

        account_data_headers = self.headers | {
            "X-CSRFToken": self.csrf,
            "X-tz-offset": str(self.tz_offset),
            "X-Ts": str(seconds),
            "X-Prot": prot_hash,
        }

        try:
            account_data_response = self.s.get(url, headers=account_data_headers)

            acc_data = account_data_response.json()

            self.account_data = {
                "company_id": acc_data["authCompany"]["companyId"],
                "name": acc_data["authCompany"]["company"],
                "money": acc_data["authCompany"]["money"],
                "simboosts": acc_data["authCompany"]["simBoosts"],
                "production_modifier": acc_data["authCompany"]["productionModifier"],
                "sales_modifier": acc_data["authCompany"]["salesModifier"],
                "rank": acc_data["authCompany"]["rank"],
                "level": acc_data["authCompany"]["level"],
            }
            self.realm_id = acc_data["authCompany"]["realmId"]
            self.economy_state = acc_data["temporals"]["economyState"]
            self.get_realm_variables()
            time.sleep(0.2)
            self.get_admin_overhead()
            time.sleep(0.2)
            self.get_owned_resources()
            time.sleep(0.2)
            self.get_buildings_state()
            time.sleep(0.2)
            self.get_company_logo(acc_data["authCompany"]["logo"])
            time.sleep(0.2)
            self.get_executives()
            time.sleep(0.2)
            self.get_csrf()

        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_buildings_state(self):
        try:
            url = "https://www.simcompanies.com/api/v2/companies/me/buildings/"
            (seconds, prot_hash) = self.generate_headers(url)
            building_state_headers = self.headers | {
                "X-CSRFToken": self.csrf,
                "X-tz-offset": str(self.tz_offset),
                "X-Ts": str(seconds),
                "X-Prot": prot_hash,
            }
            building_states_response = self.s.get(url, headers=building_state_headers)
            building_states_response.raise_for_status()
            self.account_data["buildings"] = building_states_response.json()
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_admin_overhead(self):
        try:
            url = "https://www.simcompanies.com/api/v2/companies/me/administration-overhead/"
            admin_overhead_response = self.s.get(url, headers=self.headers)
            admin_overhead_response.raise_for_status()
            self.account_data["admin_overhead"] = float(admin_overhead_response.text)

        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_executives(self):
        try:
            url = f"https://www.simcompanies.com/api/v3/companies/{self.account_data['company_id']}/executives/"
            (seconds, prot_hash) = self.generate_headers(url)
            executives_headers = self.headers | {
                "X-CSRFToken": self.csrf,
                "X-tz-offset": str(self.tz_offset),
                "X-Ts": str(seconds),
                "X-Prot": prot_hash,
            }
            executives_response = self.s.get(url, headers=executives_headers)
            executives_response.raise_for_status()
            self.executives = {}
            executives = executives_response.json()["executives"]
            for executive in executives:
                if "currentTraining" not in executive:
                    self.executives[f"c{executive['currentWorkHistory']['position']}o"] = (
                        executive
                    )
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_company_logo(self, url):
        try:
            logo_response = self.s.get(url)
            with open("logo.png", "wb") as f:
                f.write(logo_response.content)
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def print_info(self):
        console = Console()

        pil_img = Image.open("logo.png")
        pil_img = pil_img.resize((40, 40))

        img = Pixels.from_image(pil_img)

        # Right: System info
        system_info = "\n".join(
            [
                f"[bold white]Şirket Adı:[/bold white] {self.account_data['name']}",
                f"[bold white]Para:[/bold white] [green]${self.account_data['money']}[/green]",
                f"[bold white]Level:[/bold white] {self.account_data['level']}",
                f"[bold white]Sıralama:[/bold white] {self.account_data['rank']}",
                f"[bold white]Perakende Yüzdesi:[/bold white] %{self.account_data['sales_modifier']}",
                f"[bold white]Üretim Yüzdesi:[/bold white] %{self.account_data['production_modifier']}",
                f"[bold white]Yönetim giderleri:[/bold white] %{round((self.account_data['admin_overhead'] * 100) - 100,3)}",
            ]
        )

        # Wrap in panels

        left_panel = Panel(img, border_style="cyan", width=40)  # limit width
        right_panel = Panel(system_info, border_style="green", width=40)

        # left_panel = Panel(img, border_style="cyan")
        # right_panel = Panel(system_info, border_style="green")

        # Print side by side
        console.print(Columns([left_panel, right_panel]))

    def get_owned_resources(self):
        try:
            url = f"https://www.simcompanies.com/api/v3/resources/{self.account_data['company_id']}/"
            resources_owned_response = self.s.get(url, headers=self.headers)
            resources_owned_response.raise_for_status()
            self.owned_resources = resources_owned_response.json()
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_encyclopedia_resource(self, resource_id):
        try:
            url = f"https://www.simcompanies.com/api/v4/0/0/encyclopedia/resources/{self.economy_state}/{resource_id}/"
            encyclopedia_resource_response = self.s.get(url, headers=self.headers)
            encyclopedia_resource_response.raise_for_status()
            return encyclopedia_resource_response.json()
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def giris(self, e_mail: str, sifre: str):
        url = "https://www.simcompanies.com/api/v2/auth/email/auth/"
        data = json.dumps(
            {
                "authTicket": "",
                "email": e_mail,
                "password": sifre,
                "timezone_offset": self.tz_offset,
            }
        )
        (seconds, prot_hash) = self.generate_headers(url)
        login_headers = self.headers | {
            "Content-Type": "application/json",
            "Content-Length": str(len(data)),
            "X-CSRFToken": self.csrf,
            "X-tz-offset": str(self.tz_offset),
            "X-Ts": str(seconds),
            "X-Prot": prot_hash,
        }

        try:
            login_response = self.s.post(
                url,
                data=data,
                headers=login_headers,
            )
            if login_response.status_code == 200:
                print("giriş yapılıyo")
                self.get_csrf()
                self.get_account_data()
                self.print_info()
        except Exception:
            logging.error("An unexpected error occurred", exc_info=True)

    def get_market_price(self,resource_id):
        try:
            url = f"https://www.simcompanies.com/api/v3/market-ticker/{self.realm_id}/"
            market_ticker = self.s.get(url,headers=self.headers)
            market_ticker.raise_for_status()
            for resource in market_ticker.json():
                if resource["kind"] == resource_id:
                    return resource["price"]
            raise Exception("Could not find resource market price")
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_resource_object(self,resource_id):
        ## normalde resourcesdan constanttanid ile dönülecek
        return [
            self.constants["resources"][str(resource_id)],
            self.get_encyclopedia_resource(resource_id)
        ]

    def get_sale_context(self,resource_id):
        resource_info = self.get_resource_object(resource_id)
        building_info = self.constants["buildings"][resource_info[1]["soldAt"]]
        available_buildings = []
        acceleration = 1
        if self.acceleration_events is not None:
            for event in self.acceleration_events:
                if event["kind"] == resource_id:
                    acceleration = round((100 + event["speedModifier"] / 100), 2)

        resource_quality_array = [None] * 13
        for resource in self.owned_resources:
            if resource["kind"] == resource_id:
                resource_quality_array[resource["quality"]] = {"amount":resource["amount"],"cost":resource["cost"]["market"]}

        for building in self.account_data["buildings"]:
            if "busy" not in building and building["kind"] == resource_info[1]["soldAt"]:
                available_buildings.append(building)

        return resource_info,building_info,available_buildings,acceleration,resource_quality_array

    def sell_hours(self, resource_id,hours):
        resource_info, building_info,available_buildings,acceleration,resource_quality_array = self.get_sale_context(resource_id)

        for building in available_buildings:
            building_level = building["size"]
            total_quantity,info_array,total_cost = self.consume_inventory(hours,building_level,resource_id,resource_quality_array,acceleration,resource_info,building_info)
            price_to_sell = 0
            average_quality = 0
            for index,info  in enumerate(info_array):
                price_to_sell += info["cost"] * info["amount"] / total_quantity
                average_quality += index * info["amount"] / total_quantity
            price_to_sell = round(price_to_sell,1)

            print(f"info: {info_array}")
            print(f"quantity: {total_quantity}")
            print(f"price: {price_to_sell}")
            print(f"average_quality: {average_quality}")
            print(f"cost: {total_cost}")

            calculate_seconds_to_finish = calculate_profit(
            building_level,
            resource_id,
            price_to_sell,
            total_quantity,
            average_quality,
            total_cost,
            self.account_data["sales_modifier"],
            self.executives["cmo"]["skills"]["cmo"] if "cmo" in self.executives else 0,
            self.executives["coo"]["skills"]["coo"] if "coo" in self.executives else 0,
            acceleration,
            self.economy_state,
            self.account_data["admin_overhead"],
            self.weather,
            resource_info,
            building_info)
            self.sell_at_building(building["id"],resource_id,price_to_sell,total_quantity,calculate_seconds_to_finish["secondsToFinish"])

    def consume_inventory(self,hours,building_level,resource_id,resource_quality_array,acceleration,resource_info,building_info):
        total_cost = 0
        total_quantity = 0
        info_array = data = [{"cost": 0, "amount": 0} for _ in range(13)]

        print(resource_quality_array)
        highest_quality = 13
        seconds_left = hours * 3600
        while True:
            quantity = 0
            for quality in range(highest_quality-1,-1,-1):
                if resource_quality_array[quality] is not None:
                    highest_quality = quality
                    quantity = resource_quality_array[quality]["amount"]
                    cost = resource_quality_array[quality]["cost"]
                    break
            optimum_price = calculate_optimum_price(
                building_level,
                resource_id,
                highest_quality,
                quantity,
                self.executives["cmo"]["skills"]["cmo"] if "cmo" in self.executives else 0,
                self.executives["coo"]["skills"]["coo"] if "coo" in self.executives else 0,
                acceleration,
                cost,
                self.account_data["sales_modifier"],
                self.economy_state,
                self.account_data["admin_overhead"],
                self.weather,
                resource_info,
                building_info
            )
            seconds_left -= quantity * optimum_price[1]
            if seconds_left < 0:
                overshot_amount = abs(round(seconds_left / optimum_price[1]))
                if overshot_amount > 0:
                    total_quantity += quantity - overshot_amount
                    total_cost += cost / quantity * (quantity - overshot_amount)
                    info_array[quality]["amount"] = quantity - overshot_amount
                    info_array[quality]["cost"] = optimum_price[0]
                    seconds_left += overshot_amount * optimum_price[1]
                    break
            total_quantity += quantity
            info_array[quality]["amount"] = quantity
            info_array[quality]["cost"] = optimum_price[0]

        return total_quantity,info_array,total_cost

    def sell_at_building(self,building_id,resource_id,price,amount,seconds_to_finish,):
        url = f"https://www.simcompanies.com/api/v1/buildings/{building_id}/busy/"
        data = json.dumps(
            {
            "kind": resource_id,
            "amount": amount,
            "price": price,
            "estimatedSecondsToFinish": seconds_to_finish,
            }
        )
        (seconds, prot_hash) = self.generate_headers(url)
        sell_headers = self.headers | {
        "Content-Type": "application/json",
        "Content-Length": str(len(data)),
        "X-CSRFToken": self.csrf,
        "X-tz-offset": str(self.tz_offset),
        "X-Ts": str(seconds),
        "X-Prot": prot_hash,
        }
        try:
            sell_response = self.s.post(url,headers=sell_headers,data=data)
            sell_response.raise_for_status()
            print("sanırım oldu bak bakim")
        except Exception:
            logging.error("Exception occurred", exc_info=True)




menajer = SatisElemani()
menajer.giris("e-mail@gmail.com", "sifre")
menajer.sell_hours(60,24)


# YAPILACAKLAR:
# OPTİMUM FİYAT HESABI AĞIRLIKLI ORTALAMA DOĞRU MU KONTROL ET 345. SATIR PRİCE TO SELL HESABI
# ÇIKIŞ YAPMA
# BORSADAN ALIŞ BELKİ?
