import base64
import binascii
import hashlib
import json
import random
import ssl
import time

import cloudscraper
import requests
from bs4 import BeautifulSoup

from eth_account.signers.local import LocalAccount
from fake_useragent import UserAgent
from tonclient.types import NetworkConfig, ParamsOfMnemonicDeriveSignKeys, ParamsOfSign, CallSet, Signer, \
    ParamsOfEncodeMessage, Abi, ParamsOfProcessMessage

from TwitterModel import Account

def random_user_agent():
    browser_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{2}_{3}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{1}.{2}) Gecko/20100101 Firefox/{1}.{2}',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Edge/{3}.{4}.{5}'
    ]

    chrome_version = random.randint(70, 108)
    firefox_version = random.randint(70, 108)
    safari_version = random.randint(605, 610)
    edge_version = random.randint(15, 99)

    chrome_build = random.randint(1000, 9999)
    firefox_build = random.randint(1, 100)
    safari_build = random.randint(1, 50)
    edge_build = random.randint(1000, 9999)

    browser_choice = random.choice(browser_list)
    user_agent = browser_choice.format(chrome_version, firefox_version, safari_version, edge_version, chrome_build, firefox_build, safari_build, edge_build)

    return user_agent

class VenomAccount:

    def __init__(self, proxy, address, auth_token, csrf):

        self.proxy = proxy
        self.address = address
        self.auth_token = auth_token
        self.csrf = csrf


        self.session = self._make_scraper()
        self.session.proxies = {
            'http': f'http://{proxy.split(":")[2]}:{proxy.split(":")[3]}@{proxy.split(":")[0]}:{proxy.split(":")[1]}',
            'https': f'http://{proxy.split(":")[2]}:{proxy.split(":")[3]}@{proxy.split(":")[0]}:{proxy.split(":")[1]}'}
        self.session.user_agent = random_user_agent()

        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.session.headers = {'content-type': 'application/json'}


    def Login(self):

        self.session.headers.update({'wallet-address': self.address})

        with self.session.get('https://venom.network/api/auth/profile', timeout=10) as response:
            print(response.text)

        self.ConnectTwitter()

        self.TwitterAccount = Account(auth_token=self.auth_token,
                                       csrf=self.csrf,
                                       proxy=self.proxy,
                                       name='1')

        self.TwitterAccount.Follow(1489188578001309697)

        time.sleep(4)

        print(self.session.cookies)

        self.session.headers.update({'content-type': 'application/json'})
        with self.session.post('https://venom.network/api/tasks/solving/twitter', json={'taskId': 8}, timeout=10) as response:
            print(response.text)

        with self.session.post('https://venom.network/api/tasks/claim', json={"taskIds":[5,8]}, timeout=10) as response:
            print(response.text)

    def VenomTask1(self):

        with self.session.post('https://venom.network/api/tasks/solving/twitter', json={'taskId': 19}, timeout=10) as response:
            print(response.text)

        time.sleep(random.randint(100, 450)/100)

        self.TwitterAccount.Tweet(text='Just claimed my first faucet tokens and am ready to use them on the #VenomTestnet! Get them yourself on https://venom.network ')

        with self.session.post('https://venom.network/api/tasks/solving/twitter', json={'taskId': 18}, timeout=10) as response:
            print(response.text)

        # Продолжение в селене (Минт NFT)

    def VenomTask2_Transfer(self):

        # Сделать трансфер средств на этот кош 0:077873f1453fa67b0f1ce77f1e806675acd19c4694b9738be61fd406618f2f7a

        with self.session.post('https://task-api.venom.network/api/v1/project/getTaskStatus', json={"address":self.address,
                                                                                                    "projectId":1,
                                                                                                    "taskName":"Send Native Venom Token to Exact Address"}, timeout=10) as response:
            print(response.text)

        # Продолжение в селене (Минт NFT)

    def ConnectTwitter(self):

        with self.session.get('https://venom.network/api/auth/twitter/oauth/sign_in?successRedirectUri=https://venom.network/tasks&errorRedirectUri=https://venom.network/tasks',
                              timeout=15) as response:
            # print(response.text)

            oauth_token = response.text.split('oauth_token=')[-1]
            self.session.cookies.update({'auth_token': self.auth_token, 'ct0': self.csrf})
            self.session.headers.update({
                                            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                                            'x-twitter-auth-type': 'OAuth2Session',
                                            'x-csrf-token': self.csrf,
                                            'content-type':'application/x-www-form-urlencoded'})
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


def TON_Api_test():

    from tonclient.types import ClientConfig
    from tonclient.client import TonClient

    network = NetworkConfig(
        server_address='https://jrpc-testnet.venom.foundation/rpc')

    config = ClientConfig(network=network)

    client = TonClient(config=config)

    seed_phrase = ""


    # Получаем ключи из Seed phrase
    keypair = client.crypto.mnemonic_derive_sign_keys(ParamsOfMnemonicDeriveSignKeys(seed_phrase))

    message = "We appreciate your participation in the Venom Testnet. You will receive faucet tokens for taking part in the Testnet and actionable items. The Testnet tokens can be used for testnet-related activities only. Please note that the Venom Testnet Tokens have no monetary value."
    message_base64 = base64.b64encode(message.encode('utf-8')).decode('utf-8')

    signature = client.crypto.sign(ParamsOfSign(unsigned=message_base64, keys=keypair))

    bytes_str = signature.signature

    hash_object = hashlib.sha256(message.encode('utf-8'))
    hex_dig = hash_object.hexdigest()

    print(hex_dig)

    print("Подпись сообщения:", bytes_str)

    print(hashlib.sha256('s%3A-eBLpPshYOukIxkeuBpBK2sdfyc489Hw.N8X0eGHDoJKejotU82EOpNFO10vLorIfYSfbMMLfG9A'.encode('utf-8')).hexdigest())
    print(base64.b64encode(binascii.unhexlify(signature.signature)).decode('utf-8'))


def TON_Api_transfer_test(seed_phrase, recipient_address, amount):

    from tonclient.types import ClientConfig
    from tonclient.client import TonClient

    network = NetworkConfig(
        server_address='https://jrpc-testnet.venom.foundation/rpc')

    config = ClientConfig(network=network)

    client = TonClient(config=config)

    # Получаем ключи из Seed phrase
    keypair = client.crypto.mnemonic_derive_sign_keys(ParamsOfMnemonicDeriveSignKeys(seed_phrase))

    # Составьте и отправьте транзакцию
    signer = Signer.Keys(keys=keypair)
    call_set = CallSet(function_name='transfer', input={'address': recipient_address, 'amount': amount})

    # transaction = client.abi.encode_message(
    #     ParamsOfEncodeMessage(
    #         abi=Abi(),
    #         signer=signer,
    #         address='0:00869c558ee54f36b0ff6730443c344e3b756a27b93ce1d3b6569c82635a4056',
    #         call_set=call_set,
    #         processing_try_index=1
    #     )
    # )

    processing_response = client.processing.process_message(
        ParamsOfProcessMessage(
            ParamsOfEncodeMessage(
                abi=Abi.from_path('ABI.json'),
                signer=signer,
                address='0:00869c558ee54f36b0ff6730443c344e3b756a27b93ce1d3b6569c82635a4056',
                call_set=call_set,
                processing_try_index=1,
            ),
            send_events=False
        )
    )

    if processing_response['transaction']['status'] == 'failed':
        print('Транзакция не удалась:', processing_response['transaction']['id'])
    else:
        print('Транзакция успешно отправлена:', processing_response['transaction']['id'])

TON_Api_transfer_test("",
                      "",
                      "2000000000")
