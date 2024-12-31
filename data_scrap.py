from selenium.webdriver.common.by import By
from log import Bd_user_name, BD_host_name, BD_password, proxy_verification, proxy_verification2
from DB_MySQL import get_values, create_connection, create_database, execute_query, create_users_table
import re
from fake_useragent import UserAgent
from seleniumbase import SB
import itertools
import time


class ProxyRotator:
    def __init__(self, proxi_lst):
        self.proxies = itertools.cycle(proxi_lst)
        self.current_proxy = None
        self.request_counter = 0

    def change_proxy(self):
        self.current_proxy = next(self.proxies)
        self.request_counter = 0
        return self.current_proxy

    def get_proxy(self):
        if self.request_counter % 3 == 0:
            self.change_proxy()
        self.request_counter += 1
        return self.current_proxy


def main(link):
    all_detailed_links = []
    length_scroll = 0
    links = [f'{link}pn={page_num}' for page_num in range(1, 41)]
    ua = UserAgent()
    agent = f"--user-agent={ua}"
    with SB(uc=True, proxy=proxy_verification, agent=agent) as sb:
        sb.open(links[0])
        try:
            time.sleep(5)
            shadow_host = sb.execute_script("return document.querySelector('#usercentrics-root')")
            shadow_root = sb.execute_script("return arguments[0].shadowRoot", shadow_host)

            deny_button = shadow_root.find_element(By.CSS_SELECTOR, 'button[data-testid="uc-deny-all-button"]')
            if deny_button:
                deny_button.click()

        except Exception as e:
            print("error:", e)

        for link in links:
            try:
                sb.open(link)
                sb.sleep(50)
                while True:
                    detailed_link = sb.find_elements(By.CSS_SELECTOR, 'div._1lw0o5cb a')
                    for lin in detailed_link[length_scroll:]:
                        href = lin.get_attribute('href')
                        if href in all_detailed_links:
                            break
                        sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", lin)
                        all_detailed_links.append(href)
                        length_scroll += 1
            except Exception as e:
                print(f'error "{e}"')

    with SB(uc=True, protocol='https', proxy=proxy_verification2, agent=agent) as sb2:
        sb2.open(all_detailed_links[0])
        try:
            time.sleep(5)
            shadow_host = sb2.execute_script("return document.querySelector('#usercentrics-root')")
            shadow_root = sb2.execute_script("return arguments[0].shadowRoot", shadow_host)

            deny_button = shadow_root.find_element(By.CSS_SELECTOR, 'button[data-testid="uc-deny-all-button"]')
            if deny_button:
                deny_button.click()

        except Exception as e:
            print("error:", e)
        for d_link in all_detailed_links:
            try:
                sb2.open(d_link)
                sb2.sleep(2)
                price = sb2.find_element(By.CSS_SELECTOR, "p._194zg6t3").text
                info = sb2.find_elements(By.CSS_SELECTOR, "p._194zg6t8")
                details = sb2.find_elements(By.CSS_SELECTOR, "h1._194zg6t8")
                name = d_link.split("_")[1]
                match = re.search(r"£([\d,]+)", price)
                detail_str = ", ".join([str(d) for d in details])
                info_str = ", ".join([str(i) for i in info])
                price_str = match.group(1)
                price_int = int(price_str.replace(",", ""))
                get_values(name, price_int, info_str, detail_str, d_link)
            except Exception as e:
                print(f'error "{e}"')


def activate_bd():
    connect = create_connection(BD_host_name, Bd_user_name, BD_password, None)
    create_database_query = "CREATE DATABASE IF NOT EXISTS rent_price_uk"
    create_database(connect, create_database_query)
    connect = create_connection(BD_host_name, Bd_user_name, BD_password, "rent_price_uk")
    execute_query(connect, create_users_table)



print('1')
#proxy_rotator = ProxyRotator(proxies) if u have a lot of proxies
url = "***********************"
activate_bd()
main(url)

#https://www.zoopla.co.uk/to-rent/property/london/?price_frequency=per_month&q=London&search_source=home&=pn=1
