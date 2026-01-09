import io
import json
import logging
import os
import sys
import time
from os import getenv
from threading import ExceptHookArgs

os.environ["PYTHONUTF8"] = "1"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import requests
from dotenv import load_dotenv
from requests.models import HTTPError

from hash import lXt_py
from profitCalculator import find_optimal_sale_for_hours

RESOURCE_ID = 60


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
            self.logo_url = acc_data["authCompany"]["logo"]
            self.get_realm_variables()
            time.sleep(0.2)
            self.get_admin_overhead()
            time.sleep(0.2)
            self.get_owned_resources()
            time.sleep(0.2)
            self.get_buildings_state()
            time.sleep(0.2)
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
                    self.executives[
                        f"c{executive['currentWorkHistory']['position']}o"
                    ] = executive
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def print_info(self):
        account_info = "\n".join(
            [
                "",
                f"Şirket Adı: {self.account_data['name']}",
                f"Para: ${self.account_data['money']}",
                f"Level: {self.account_data['level']}",
                f"Sıralama: {self.account_data['rank']}",
                f"Perakende Yüzdesi (temel): %{self.account_data['sales_modifier']}",
                f"Üretim Yüzdesi (temel): %{self.account_data['production_modifier']}",
                f"Yönetim giderleri (temel): %{round((self.account_data['admin_overhead'] * 100) - 100, 3)}",
                "",
            ]
        )

        print(account_info)

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

    def get_market_price(self, resource_id):
        try:
            url = f"https://www.simcompanies.com/api/v3/market-ticker/{self.realm_id}/"
            market_ticker = self.s.get(url, headers=self.headers)
            market_ticker.raise_for_status()
            for resource in market_ticker.json():
                if resource["kind"] == resource_id:
                    return resource["price"]
            raise Exception("Could not find resource market price")
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def get_resource_object(self, resource_id):
        return [
            self.constants["resources"][str(resource_id)],
            self.get_encyclopedia_resource(resource_id),
        ]

    def get_resource_quality_array(self, resource_id):
        self.get_owned_resources()
        resource_quality_array = [None] * 13
        for resource in self.owned_resources:
            if resource["kind"] == resource_id and not resource["blocked"]:
                resource_quality_array[resource["quality"]] = {
                    "amount": resource["amount"],
                    "cost": resource["cost"]["market"],
                }
        return resource_quality_array

    def get_sale_context(self, resource_id):
        resource_info = self.get_resource_object(resource_id)
        building_info = self.constants["buildings"][resource_info[1]["soldAt"]]
        available_buildings = []
        building_types = []
        acceleration = 1
        if self.acceleration_events is not None:
            for event in self.acceleration_events:
                if event["kind"] == resource_id:
                    acceleration = round((100 + event["speedModifier"] / 100), 2)
        for building in self.account_data["buildings"]:
            building_types.append(building["kind"])
            if (
                "busy" not in building
                and building["kind"] == resource_info[1]["soldAt"]
            ):
                # if  building["kind"] == resource_info[1]["soldAt"]: # for testing
                available_buildings.append(building)
        print(f"Ürünün satılacağı bina tipi: {resource_info[1]['soldAt']}")
        print(f"Bulunan binaların tipleri: {building_types}")
        return (
            resource_info,
            building_info,
            available_buildings,
            acceleration,
        )

    def sell_hours(self, resource_id, hours):
        (
            resource_info,
            building_info,
            available_buildings,
            acceleration,
        ) = self.get_sale_context(resource_id)
        print(f"{len(available_buildings)} Binada satış yapılacak.")

        for building in available_buildings:
            building_level = building["size"]
            resource_quality_array = self.get_resource_quality_array(resource_id)
            print(
                "Elimizdeki ürünler: ",
                resource_quality_array,
                "\n",
            )
            (
                total_quantity,
                total_cost,
                optimum_price,
                seconds_to_finish,
                average_quality,
                wages,
            ) = find_optimal_sale_for_hours(
                hours,
                building_level,
                resource_id,
                resource_quality_array,
                self.account_data["sales_modifier"],
                self.executives["cmo"]["skills"]["cmo"]
                if "cmo" in self.executives
                else 0,
                self.executives["coo"]["skills"]["coo"]
                if "coo" in self.executives
                else 0,
                self.economy_state,
                self.account_data["admin_overhead"],
                self.weather,
                acceleration,
                resource_info,
                building_info,
                self.constants["core"],
            )
            print(f"Miktar: {total_quantity}")
            print(f"Satılan Fiyat: {optimum_price}$")
            print(f"Ortalama kalite: {average_quality}")
            print(f"Satılan Malların Maliyeti: {total_cost}$")
            print(f"Satış Süresi (saniye): {seconds_to_finish}")
            print(f"Ödenen maaşlar: {wages}$")

            self.sell_at_building(
                building["id"],
                resource_id,
                optimum_price,
                total_quantity,
                seconds_to_finish,
            )

        print("Başarım kontrol ediliyor...")
        print("Başarım Alındı" if self.basarim_kontrol() else "Başarım alınamadı","\n")
        print("Çıkış Yapılıyor...")
        print("Çıkış yapıldı" if self.cikis_yap() else "Çıkış Yapılamadı")


    def basarim_kontrol(self):
        try:
            basarim_url = "https://www.simcompanies.com/api/v2/no-cache/companies/me/achievements/"
            (seconds, prot_hash) = self.generate_headers(basarim_url)
            basarim_headers = self.headers | {
                "X-CSRFToken": self.csrf,
                "X-tz-offset": str(self.tz_offset),
                "X-Ts": str(seconds),
                "X-Prot": prot_hash,
            }
            basarim_response = self.s.get(basarim_url, headers=basarim_headers)
            basarim_response.raise_for_status()
            basarim_response_json = basarim_response.json()
            for basarim in basarim_response_json:
                if basarim["id"] == "prd-sold":
                    return self.basarim_al()
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def basarim_al(self):
        try:
            basarim_al_url = "https://www.simcompanies.com/api/v2/no-cache/companies/achievements/prd-sold/"
            (seconds, prot_hash) = self.generate_headers(basarim_al_url)
            basarim_al_headers = self.headers | {
                "X-CSRFToken": self.csrf,
                "X-tz-offset": str(self.tz_offset),
                "X-Ts": str(seconds),
                "X-Prot": prot_hash,
            }
            basarim_al_response = self.s.delete(basarim_al_url, headers=basarim_al_headers)
            basarim_al_response.raise_for_status()
            return True
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    def cikis_yap(self):
        try:
            cikis_url = "https://www.simcompanies.com/signout/"
            cikis_response = self.s.get(cikis_url)
            cikis_response.raise_for_status()
            return True
        except Exception:
            logging.error("Exception occurred", exc_info=True)


    def sell_at_building(
        self,
        building_id,
        resource_id,
        price,
        amount,
        seconds_to_finish,
    ):
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
            sell_response = self.s.post(url, headers=sell_headers, data=data)
            sell_response.raise_for_status()
            print("sanırım oldu bak bakim")
            print("\n\n")
            time.sleep(0.5)
        except Exception:
            logging.error("Exception occurred", exc_info=True)


requested_hours = eval(sys.argv[1])
print(f"{requested_hours} saatlik satış yapılacak")
load_dotenv()


resource_id_num = sys.argv[2] if len(sys.argv) > 2 else RESOURCE_ID
print(f"Satılan Item ID: {resource_id_num}")

menajer = SatisElemani()
menajer.giris(getenv("E-MAIL"), getenv("PASSWORD"))
menajer.sell_hours(int(resource_id_num), requested_hours)


# YAPILACAKLAR:
