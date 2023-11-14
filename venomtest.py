import traceback
import zipfile
from time import sleep
import json
import pyperclip
from capmonster_python import HCaptchaTask
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import ssl
import cloudscraper
import requests
from bs4 import BeautifulSoup
from TwitterModel import Account

url_first = r"https://www.google.ru/"
url_site = r"https://venom.network/tasks"

# List of proxies to be used
proxy_list = [line.strip() for line in open("Proxy.txt", "r")]

# List of proxies to be used
# private_key_list = [line.strip() for line in open("Private_key.txt", "r")]

with open("data.txt", "r") as file:
    TOKEN = file.read()



auth_token = ""
csrf = ""
current_seed = ""


def random_user_agent():
    chrome_version = random.randint(70, 108)
    build = random.randint(1000, 9999)
    user_agent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.{build}.{build} Safari/537.36'
    return user_agent


def acp_api_send_request(driver, message_type, data=None):
    if data is None:
        data = {}
    message = {
        'receiver': 'antiCaptchaPlugin',
        'type': message_type,
        **data
    }
    return driver.execute_script("""
	return window.postMessage({});
	""".format(json.dumps(message)))


def get_chromedriver(use_proxy=False, user_agent=None, proxy=None, extension=False):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=900,900")

    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'
        PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = proxy.split(":")

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"76.0.0"
        }
        """

        background_js = """
        let config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={random_user_agent()}')

    if extension:
        # chrome_options.add_extension(f'Extension/Rabby_wallet.crx')
        chrome_options.add_extension(f'Extension/Venom_wallet.crx')
        # chrome_options.add_extension(f"Extension/anticaptcha-plugin_v0.63.crx")

    s = Service(executable_path=f'Extension/chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=chrome_options)

    return driver


class VenomAccount:

    def __init__(self, current_proxy, copy_address_venom, auth_token, csrf):

        self.current_proxy = current_proxy
        self.copy_address_venom = copy_address_venom
        self.auth_token = auth_token
        self.csrf = csrf
        self.TwitterAccount = Account(auth_token=self.auth_token,
                                      csrf=self.csrf,
                                      proxy=self.current_proxy,
                                      name='1')

        self.session = self._make_scraper()
        self.session.proxies = {
            'http': f'http://{current_proxy.split(":")[2]}:{current_proxy.split(":")[3]}@{current_proxy.split(":")[0]}:{current_proxy.split(":")[1]}',
            'https': f'http://{current_proxy.split(":")[2]}:{current_proxy.split(":")[3]}@{current_proxy.split(":")[0]}:{current_proxy.split(":")[1]}'}
        self.session.user_agent = random_user_agent()

        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.session.headers = {'content-type': 'application/json'}

    def SolveCaptcha(self):

        capmonster = HCaptchaTask("?????????????????")
        task_id = capmonster.create_task("https://venom.network/", "106e57f5-f9fd-4ac7-b086-ad720846f181")
        result = capmonster.join_task_result(task_id)
        return result['gRecaptchaResponse']

    def Login(self):

        print("Login - start")
        self.session.headers.update({'wallet-address': self.copy_address_venom})

        with self.session.get('https://venom.network/api/auth/profile', timeout=10) as response:
            print(response.text)

        self.ConnectTwitter()

        self.TwitterAccount.Follow(1489188578001309697)

        sleep(4)

        print(self.session.cookies)

        self.session.headers.update({'content-type': 'application/json'})
        with self.session.post('https://venom.network/api/tasks/solving/twitter', json={'taskId': 8},
                               timeout=10) as response:
            print(response.text)
        # ------------
        with self.session.post('https://venom.network/api/tasks/claim', json={"taskIds": [5, 8]},
                               timeout=10) as response:
            print(response.text)

        print("Login - end")

    def VenomTask1(self):
        print("ConnectWalletSite - twitter start")

        self.TwitterAccount.Follow(1624739329447788546)

        with self.session.post('https://venom.network/api/tasks/solving/twitter', json={'taskId': 19},
                               timeout=10) as response:
            print(response.text)

        sleep(random.randint(100, 450) / 100)

        self.TwitterAccount.Tweet(
            text='Just claimed my first faucet tokens and am ready to use them on the #VenomTestnet! Get them yourself on https://venom.network ')

        with self.session.post('https://venom.network/api/tasks/solving/twitter', json={'taskId': 18},
                               timeout=10) as response:
            print(response.text)

        print("ConnectWalletSite - twitter end")
        # Продолжение в селене (Минт NFT)

    def VenomTask1_Transfer(self):

        # Сделать трансфер средств на этот кош 0:077873f1453fa67b0f1ce77f1e806675acd19c4694b9738be61fd406618f2f7a

        with self.session.post('https://task-api.venom.network/api/v1/project/getTaskStatus',
                               json={"address": self.copy_address_venom,
                                     "projectId": 1,
                                     "taskName": "Send Native Venom Token to Exact Address"}, timeout=10) as response:
            print(response.text)

        # Продолжение в селене (Минт NFT)

    def ConnectTwitter(self):

        HCaptchaToken = self.SolveCaptcha()
        self.session.headers.update({'h-captcha': HCaptchaToken})

        with self.session.get(
                'https://venom.network/api/auth/twitter/oauth/sign_in?successRedirectUri=https://venom.network/tasks&errorRedirectUri=https://venom.network/tasks',
                timeout=15) as response:
            print(response)  # Print the response object
            if response is not None:
                print(response.text)  # Print the response content if available
            else:
                print("Response is None")

            oauth_token = response.text.split('oauth_token=')[-1]
            self.session.cookies.update({'auth_token': self.auth_token, 'ct0': self.csrf})
            self.session.headers.update({
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'x-twitter-auth-type': 'OAuth2Session',
                'x-csrf-token': self.csrf,
                'content-type': 'application/x-www-form-urlencoded'})
            with self.session.get(
                    f'https://api.twitter.com/oauth/authenticate?oauth_token={oauth_token}',
                    timeout=15) as response:
                soup = BeautifulSoup(response.text, 'html.parser')
                authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
                payload = {'authenticity_token': authenticity_token,
                           'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
                           'oauth_token': oauth_token}
                # self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                with self.session.post(f'https://api.twitter.com/oauth/authorize', data=payload, timeout=15,
                                       allow_redirects=False) as response:
                    # self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                    soup = BeautifulSoup(response.text, 'html.parser')
                    link = soup.find('a', class_='maintain-context').get('href')
                    print(link)
                    with self.session.get(link, timeout=15) as response:
                        if response.ok:
                            with self.session.get('https://venom.network/tasks', timeout=10) as response:

                                if response.ok:
                                    print(f'Twitter successfully connected')
                                    return True
                        else:
                            print(f'Twitter connection failed')
                            return False

    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )


class VenomBot:
    def __init__(self):
        self.auth_token = auth_token
        self.csrf = csrf
        self.proxy_list = proxy_list
        # self.private_key_list = private_key_list
        self.current_proxy = None
        self.current_private_key = None
        self.driver = None
        self.wait = None
        self.actions = None
        self.venom_account = None

    def open_browsers(self):
        self.current_proxy = self.proxy_list.pop(0)
        # self.current_private_key = self.private_key_list.pop(0)
        # Getting to work
        sleep(0.5)
        self.driver = get_chromedriver(use_proxy=True,
                                       user_agent=random_user_agent(),
                                       proxy=self.current_proxy,
                                       extension=True)
        self.driver.set_window_position(0, 0)
        self.driver.implicitly_wait(20)  # seconds
        self.wait = WebDriverWait(self.driver, 20)
        self.actions = ActionChains(self.driver)
        # wait_long = WebDriverWait(driver, 350)

        # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": '''
        #                                             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        #                                             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        #                                             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        #                                         '''
        # })
        sleep(2)
        self.driver.get(url_first)

    def connect_anticaptcha(self):
        sleep(2)
        self.driver.get(r'https://antcpt.com/blank.html')
        sleep(1)
        acp_api_send_request(self.driver, 'setOptions', {'options': {'antiCaptchaApiKey': TOKEN}})
        sleep(3)
        self.driver.switch_to.window(self.driver.window_handles[0])
        sleep(1)

    def login_in_rabbywallet(self):
        url_rabby = r"chrome-extension://fcoecdcgjbggcbmaagdaeiafenckmbao/popup.html"

        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.get(url_rabby)
        sleep(2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/section/footer/button").click()
        sleep(0.2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/section/footer/a/button").click()
        sleep(0.2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/div[3]/div[2]/div").click()
        sleep(0.2)
        password_field = self.driver.find_element(By.ID, 'password')
        sleep(0.2)
        password_field.send_keys("12345678")
        sleep(0.2)
        confirm_password = self.driver.find_element(By.ID, 'confirmPassword')
        sleep(0.2)
        confirm_password.send_keys("12345678")
        sleep(0.2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/div/div/form/div[3]/button").click()
        sleep(0.2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/div[2]/div[2]/div[3]").click()
        sleep(0.2)
        print(self.current_private_key)
        input_private_key = self.driver.find_element(By.XPATH,
                                                     r"/html/body/div/div/form/div[2]/div/div[1]/div/div/div/input")
        sleep(0.2)
        input_private_key.send_keys(self.current_private_key)
        sleep(0.2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/form/div[3]/div/button/span").click()
        sleep(0.2)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div/form/div[3]/div/button").click()
        sleep(0.4)
        self.driver.find_element(By.XPATH,
                                 r"/html/body/div[2]/div/div[2]/div/div[2]/button").click()

    def login_in_venom(self):
        url_venom = r"chrome-extension://hepnjajijbagnlkbaegaabegmhfldljg/popup.html"

        # seed_list = []
        # # Read the proxy from a file
        # with open("Test_seed.txt", "r") as f:
        #     for line in f:
        #         seed_list.append(line.strip())
        #
        # current_seed = seed_list.pop(0)

        self.driver.find_element(By.XPATH,
                                 r"/html/body/div/div[1]/div/div[2]/div/div/div[3]/div/div[1]/button").click()
        sleep(0.2)
        click_accept = self.wait.until(
            EC.presence_of_element_located((By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div/div[2]/label/span")))
        self.actions.move_to_element(click_accept).perform()
        click_accept.click()
        click_submit = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div/div[3]/button[1]/div")))
        self.actions.move_to_element(click_submit).perform()
        click_submit.click()
        # Copy seed
        copy_seed = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div/button[2]")))
        self.actions.move_to_element(copy_seed).perform()
        copy_seed.click()
        copy_seed_phrase = pyperclip.paste()
        print(copy_seed_phrase)
        click_back = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div/button[3]")))
        self.actions.move_to_element(click_back).perform()
        click_back.click()
        click_back2 = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div/div[3]/button[2]")))
        self.actions.move_to_element(click_back2).perform()
        click_back2.click()
        click_sign_seed = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div/div[3]/div/div[2]/button")))
        self.actions.move_to_element(click_sign_seed).perform()
        click_sign_seed.click()
        words = current_seed.split()
        # words = copy_seed_phrase.split()
        elms = self.driver.find_elements(By.XPATH,
                                         r"/html/body/div/div[1]/div/div[2]/div/form/div/div[1]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[2]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[3]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[4]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[5]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[6]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[7]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[8]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[9]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[10]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[11]/div/input")
        elms += self.driver.find_elements(By.XPATH,
                                          r"/html/body/div/div[1]/div/div[2]/div/form/div/div[12]/div/input")
        for word, element in zip(words, elms):
            element.send_keys(word)
        click_conf = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div[2]/button[1]")))
        self.actions.move_to_element(click_conf).perform()
        click_conf.click()
        password_field = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="Your password"]')))
        self.actions.move_to_element(password_field).perform()
        password_field.click()
        password_field.send_keys("12345678")
        confirm_password = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="Confirm password"]')))
        self.actions.move_to_element(confirm_password).perform()
        confirm_password.click()
        confirm_password.send_keys("12345678")
        click_sign = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div[1]/div/div[2]/div/div[2]/button[1]")))
        self.actions.move_to_element(click_sign).perform()
        click_sign.click()
        sleep(3)
        self.driver.get(url_venom)
        sleep(2)
        copy_address = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div[1]/div/div[1]/div[2]/div[1]/div/div[1]/div/div/div[1]/div[2]/div[1]/span")))
        self.actions.move_to_element(copy_address).perform()
        copy_address.click()
        self.copy_address_venom = pyperclip.paste()
        print(self.copy_address_venom)
        print(f"{self.copy_address_venom}:{current_seed}")
        # print(f"{self.copy_address_venom}:{copy_seed_phrase}")
        # with open("Venom_wallet_data.txt", "a") as file:
        #     file.write(f'{self.copy_address_venom}:{copy_seed_phrase}\n')
        # print(f'{self.copy_address_venom}:{copy_seed_phrase}\n')

    def connect_wallet_site(self):
        print("connect_wallet_site - start selenium")
        self.driver.execute_script("window.open('');")
        sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.get(url_site)
        sleep(5)
        webdriver.support.wait.WebDriverWait(self.driver, 120).until(
            lambda x: x.find_element(By.CSS_SELECTOR, '.antigate_solver.solved'))
        click_connect_wallet = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div[1]/div[2]/section/div/div[1]/div/div[1]/span")))
        self.actions.move_to_element(click_connect_wallet).perform()
        click_connect_wallet.click()
        click_chrome_ext = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/a/div/div/div[2]/div")))
        self.actions.move_to_element(click_chrome_ext).perform()
        num_of_windows = len(self.driver.window_handles)
        click_chrome_ext.click()
        self.wait.until(EC.number_of_windows_to_be(num_of_windows + 1))
        self.driver.switch_to.window(self.driver.window_handles[1])
        click_connect = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, r"/html/body/div/div/div/footer/div[2]/button")))
        self.actions.move_to_element(click_connect).perform()
        num_of_windows = len(self.driver.window_handles)
        click_connect.click()
        self.wait.until(EC.number_of_windows_to_be(num_of_windows - 1))
        self.driver.switch_to.window(self.driver.window_handles[0])
        sleep(3)
        print("connect_wallet_site - end selenium")

    # def task1selen(self):

    def run(self):
        # Run the loop as long as there is data from the files
        errors = []
        while proxy_list:
            try:
                # init browsers
                self.open_browsers()
                print("Browser open")
                # connect captcha
                # self.connect_anticaptcha()
                # print("Captcha connect")
                # Open Rabby
                # self.login_in_rabbywallet()
                # print("Rabby login wallet - done")
                sleep(2)
                self.driver.switch_to.window(self.driver.window_handles[1])
                sleep(1)
                self.login_in_venom()
                print("Venom login wallet - done")
                # self.connect_wallet_site()
                sleep(2)
                print("Start....")
                # print(self.current_proxy, self.copy_address_venom, self.auth_token, self.csrf)
                # input()
                self.venom_account = VenomAccount(self.current_proxy,
                                                  self.copy_address_venom,
                                                  self.auth_token,
                                                  self.csrf)
                print("Login - start")
                self.venom_account.Login()
                print("Login - end")
                print("Start Task1")
                self.venom_account.VenomTask1()
                sleep(3)
                self.connect_wallet_site()


                sleep(10000)

            except Exception as ex:

                traceback.print_exc()

                errors.append(ex)
                input()

            if not errors:
                with open("results.txt", "a") as file:
                    file.write(f'Not Error: {self.current_proxy}\n')
                print(f'Not Error: {self.current_proxy}')
                if self.driver is not None:
                    self.driver.quit()
                continue
            else:
                with open("results.txt", "a") as file:
                    file.write(f"{self.current_proxy}:Error.\n")
                print(f"{self.current_proxy}:Error.")
                if self.driver is not None:
                    self.driver.quit()
                continue

if __name__ == '__main__':
    print("Script run...")

    # SolveCaptcha()
    # input()

    bot = VenomBot()
    bot.run()
