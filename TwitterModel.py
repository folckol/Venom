import base64
import json
import os
import random
import sqlite3
import ssl
import string
import time
import urllib
from pprint import pprint
from uuid import uuid4

import cloudscraper
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

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

class Account:

    def __init__(self, auth_token, csrf, proxy, name):

        self.name = name

        proxy_log = proxy.split(':')[2]
        proxy_pass = proxy.split(':')[3]
        proxy_ip = proxy.split(':')[0]
        proxy_port = proxy.split(':')[1]

        self.session = self._make_scraper()
        self.session.proxies = {'http': f'http://{proxy_log}:{proxy_pass}@{proxy_ip}:{proxy_port}',
                           'https': f'http://{proxy_log}:{proxy_pass}@{proxy_ip}:{proxy_port}'}
        self.session.user_agent = random_user_agent()

        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        authorization_token = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

        self.csrf = csrf
        self.auth_token = auth_token
        self.cookie = f'auth_token={self.auth_token}; ct0={self.csrf}'

        liketweet_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {authorization_token}',
            'x-csrf-token': self.csrf,
            'cookie': self.cookie
        }

        self.session.headers.update(liketweet_headers)

        # print('Аккаунт готов')


    def execute_tasks(self, RaffleInfo):

        tweetId = RaffleInfo['Link'].split('/')[-1].strip('?s=20')
        self.status = 'Success'

        if RaffleInfo['LikeStatus']:
            self.Like(tweetId)
            time.sleep(random.randint(100,350)/100)

        if RaffleInfo['RetweetStatus']:
            self.Retweet(tweetId)
            time.sleep(random.randint(100, 350) / 100)

        for i in RaffleInfo['FollowIds']:
            status = self.Follow(self.Get_User_Id(i.strip('@')))

            if status == 'ban':
                self.status = 'Account Banned'
                break

            time.sleep(random.randint(100, 350) / 100)

        if RaffleInfo['CommentStatus']:

            tweetText = ''
            CommentData = RaffleInfo['CommentData']

            if len(CommentData['Sentences']) != 0:
                tweetText += random.choice(CommentData['Sentences'])+'\n\n'

            if CommentData['MaxTags'] != 0:
                maxTags = CommentData['MaxTags']
                minTags = CommentData['MinTags']

                if minTags == maxTags:
                    tagsCount = minTags
                else:
                    tagsCount = random.choice(minTags, maxTags+1)

                used = []

                while len(used) != tagsCount:

                    r = random.choice(CommentData['Friends'])
                    if r not in used:
                        used.append(r)

                        tweetText += f"@{r.strip('@')} "

            self.Reply(tweetId, tweetText)

        return self.status


    # Основные функции твиттер аккаунта

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


    def Like(self, id):

        # print('asdsd')

        payload = {
            "variables": {
                "tweet_id": str(id)
            },
            "queryId": "lI07N6Otwv1PhnEgXILM7A"
        }

        with self.session.post("https://api.twitter.com/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",  json=payload, timeout=5) as response:
            if response.ok:
                # print(response.text)
                pass

    def Retweet(self, id):
        payload = {
            "variables": {
                "tweet_id": str(id)
            },
            "queryId": "ojPdsZsimiJrUGLR1sjUtA"
        }

        with self.session.post("https://api.twitter.com/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet", json=payload, timeout=30) as response:
            if response.ok:
                # print(response.text)
                pass

    def Follow(self, user_id):

        self.session.headers.update({'Content-Type': 'application/json'})

        with self.session.post(f"https://api.twitter.com/1.1/friendships/create.json?user_id={user_id}&follow=True", timeout=30) as response:
            print(response.text)

            if 'suspended' in response.text:
                print(f'Аккаунт {self.name} забанен')
                return 'ban'
            else:
                return 1

    def Tweet(self, text, mediaId = None):

        if mediaId == None:

            payload = {"variables":{
                        "tweet_text":text,
                        "dark_request":False,
                        "media":{
                            "media_entities":[], # {'media_id': ..., 'tagged_users': []}
                            "possibly_sensitive":False
                        },
                        "withDownvotePerspective":False,
                        "withReactionsMetadata":False,
                        "withReactionsPerspective":False,
                        "withSuperFollowsTweetFields":True,
                        "withSuperFollowsUserFields":True,
                        "semantic_annotation_ids":[]
                    },"features":{
                        "tweetypie_unmention_optimization_enabled":True,
                        "vibe_api_enabled":True,
                        "responsive_web_edit_tweet_api_enabled":True,
                        "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
                        "view_counts_everywhere_api_enabled":True,
                        "longform_notetweets_consumption_enabled":True,
                        "tweet_awards_web_tipping_enabled":False,
                        "interactive_text_enabled":True,
                        "responsive_web_text_conversations_enabled":False,
                        "responsive_web_twitter_blue_verified_badge_is_enabled":True,
                        "responsive_web_graphql_exclude_directive_enabled":False,
                        "verified_phone_label_enabled":False,
                        "freedom_of_speech_not_reach_fetch_enabled":False,
                        "standardized_nudges_misinfo":True,
                        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,
                        "responsive_web_graphql_timeline_navigation_enabled":True,
                        "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
                        "responsive_web_enhance_cards_enabled":False
                    },
                        "queryId":"Tz_cZL9zkkY2806vRiQP0Q"
                    }

            with self.session.post("https://api.twitter.com/graphql/Tz_cZL9zkkY2806vRiQP0Q/CreateTweet", json=payload,
                                   timeout=30) as response:

                print(response.text)

        else:

            payload = {"variables": {
                "tweet_text": text,
                "dark_request": False,
                "media": {
                    "media_entities": [{'media_id': str(self.Upload_image(f'{mediaId}.jpg')), 'tagged_users': []}],  # {'media_id': ..., 'tagged_users': []}
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": []
            }, "features":
                {"tweetypie_unmention_optimization_enabled":True,
                "vibe_api_enabled":True,
                "responsive_web_edit_tweet_api_enabled":True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
                "view_counts_everywhere_api_enabled":True,
                "longform_notetweets_consumption_enabled":True,
                "tweet_awards_web_tipping_enabled":False,
                "interactive_text_enabled":True,
                "responsive_web_text_conversations_enabled":False,
                "longform_notetweets_rich_text_read_enabled":True,
                "blue_business_profile_image_shape_enabled":True,
                "responsive_web_graphql_exclude_directive_enabled":True,
                "verified_phone_label_enabled":False,
                "freedom_of_speech_not_reach_fetch_enabled":False,
                "standardized_nudges_misinfo":True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,
                "responsive_web_graphql_timeline_navigation_enabled":True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
                "responsive_web_enhance_cards_enabled":False},
                "queryId": "7TKRKCPuAGsmYde0CudbVg"
            }

            self.session.headers.update({'content-type': 'application/json'})
            with self.session.post("https://api.twitter.com/graphql/7TKRKCPuAGsmYde0CudbVg/CreateTweet", json=payload,
                                   timeout=30) as response:

                print(response.text)




    def Get_Tweets(self):

        payload = {"variables":{
            "count":18,
            "includePromotedContent":True,
            "latestControlAvailable":True,
            "requestContext":"launch",
            "withCommunity":True,
            "withSuperFollowsUserFields":True,
            "withDownvotePerspective":False,
            "withReactionsMetadata":False,
            "withReactionsPerspective":False,
            "withSuperFollowsTweetFields":True,
            "seenTweetIds": random.choice(['1628168662434689025','1627790247697305602','1628338977936928770','1628141765491318785','1627793011957727232','1628217245439754241','1628126347049504783','1628321005264404480','1628263943125848066','1628157328137818112','1628070571685859328','1628092190340825094','1628169643281027072','1628310791261929477','1628324919288205312','1627662886947651587','1628152638318723072','1628357899453104129','1628168590510944256','1628125031858581504','1628121601496449026','1628192654340005889','1628158959940149248','1628355343716864000','1628092196594253829','1628218393546354690','1628368102458294273','1628227520276402179','1628294490414014464','1628364120213934082'])
        },
            "features":{
                "responsive_web_twitter_blue_verified_badge_is_enabled":True,
                "responsive_web_graphql_exclude_directive_enabled":False,
                "verified_phone_label_enabled":False,
                "responsive_web_graphql_timeline_navigation_enabled":True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
                "tweetypie_unmention_optimization_enabled":True,
                "vibe_api_enabled":True,
                "responsive_web_edit_tweet_api_enabled":True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
                "view_counts_everywhere_api_enabled":True,
                "longform_notetweets_consumption_enabled":True,
                "tweet_awards_web_tipping_enabled":False,
                "freedom_of_speech_not_reach_fetch_enabled":False,
                "standardized_nudges_misinfo":True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,
                "interactive_text_enabled":True,
                "responsive_web_text_conversations_enabled":False,
                "responsive_web_enhance_cards_enabled":False
            }
            ,"queryId":"D8Tklm7zoICDtod5RCC6qg"
        }

        recomend_tweets = []
        with self.session.post('https://api.twitter.com/graphql/D8Tklm7zoICDtod5RCC6qg/HomeTimeline', json=payload, timeout=5) as response:

            # print(response.text)

            data = response.json()['data']['home']['home_timeline_urt']['instructions'][0]['entries']
            for i in data:
                recomend_tweets.append(i['entryId'].split('-')[-1])


        # print(recomend_tweets, len(recomend_tweets))
        return recomend_tweets

    def Reply(self, tweet_id, text):

        payload = {"variables":{
            "tweet_text":text,
            "reply":{
                "in_reply_to_tweet_id":tweet_id,
                "exclude_reply_user_ids":[]
            },"dark_request":False,
            "media":{
                "media_entities":[],
                "possibly_sensitive":False
            },"withDownvotePerspective":False,
            "withReactionsMetadata":False,
            "withReactionsPerspective":False,
            "withSuperFollowsTweetFields":True,
            "withSuperFollowsUserFields":True,
            "semantic_annotation_ids":[]
        },"features":{
            "tweetypie_unmention_optimization_enabled":True,
            "vibe_api_enabled":True,
            "responsive_web_edit_tweet_api_enabled":True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
            "view_counts_everywhere_api_enabled":True,
            "longform_notetweets_consumption_enabled":True,
            "tweet_awards_web_tipping_enabled":False,
            "interactive_text_enabled":True,
            "responsive_web_text_conversations_enabled":False,
            "responsive_web_twitter_blue_verified_badge_is_enabled":True,
            "responsive_web_graphql_exclude_directive_enabled":False,
            "verified_phone_label_enabled":False,
            "freedom_of_speech_not_reach_fetch_enabled":False,
            "standardized_nudges_misinfo":True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,
            "responsive_web_graphql_timeline_navigation_enabled":True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
            "responsive_web_enhance_cards_enabled":False
        },"queryId":"Tz_cZL9zkkY2806vRiQP0Q"
        }


        with self.session.post('https://api.twitter.com/graphql/Tz_cZL9zkkY2806vRiQP0Q/CreateTweet', json=payload, timeout=10) as response:
            pass



    def Get_Connects(self):

        link = 'https://api.twitter.com/graphql/EuyIPJh9wCWkZRninDU6Uw/ConnectTabTimeline?variables=%7B%22count%22%3A20%2C%22context%22%3A%22%7B%7D%22%2C%22withSuperFollowsUserFields%22%3Atrue%2C%22withDownvotePerspective%22%3Afalse%2C%22withReactionsMetadata%22%3Afalse%2C%22withReactionsPerspective%22%3Afalse%2C%22withSuperFollowsTweetFields%22%3Atrue%7D&features=%7B%22responsive_web_twitter_blue_verified_badge_is_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Afalse%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22vibe_api_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Afalse%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Afalse%2C%22interactive_text_enabled%22%3Atrue%2C%22responsive_web_text_conversations_enabled%22%3Afalse%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D'


        peoples = []
        with self.session.get(link, timeout=10) as response:
            data = response.json()['data']['connect_tab_timeline']['timeline']['instructions'][2]['entries'][0]['content']['items']
            for i in data:
                try:
                    peoples.append(i['entryId'].split('-')[-1])
                except:
                    pass

        # print(peoples, len(peoples))
        return peoples

    def Upload_image(self, path):

        path = path
        filename = path.split('/')[-1]

        with open(path, 'rb') as f:
            data = f.read()
        data1 = base64.b64encode(data)
        message = {'media': data}
        # print(type(data))

        sizr = os.path.getsize(path)
        print(os.path.getsize(path))

        # print(len(data))
        # input()


        payload = {'command': 'INIT',
                   'total_bytes': os.path.getsize(path),
                   'media_type': 'image/jpeg'
                   }

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        with self.session.post(f'https://upload.twitter.com/1.1/media/upload.json', data=payload, timeout=30) as response:
            print(response.text)

            media_id = response.json()['media_id']



            media_id_bytes = str(media_id).encode('utf-8')

            boundary = "--{0}".format(uuid4().hex).encode('utf-8')
            self.session.headers.update({'content-type': 'multipart/form-data; boundary={0}'.format(
                boundary.decode('utf8')[2:]
            )})

            body = [
                boundary,
                b'Content-Disposition: form-data; name="command"',
                b'',
                b'APPEND',
                boundary,
                b'Content-Disposition: form-data; name="media_id"',
                b'',
                media_id_bytes,
                boundary,
                b'Content-Disposition: form-data; name="segment_index"',
                b'',
                str(0).encode('utf-8'),
                boundary,
                'Content-Disposition: form-data; name="media"; filename="{0!r}"'.format(filename).encode('utf8'),
                b'Content-Type: application/octet-stream',
                b'',
                data,
                boundary + b'--'
            ]
            body_data = b'\r\n'.join(body)

            with self.session.post(f'https://upload.twitter.com/1.1/media/upload.json', data=body_data,
                                   timeout=20) as response:
                print(response.text)
                print(response.status_code)

                payload = {'command': 'FINALIZE',
                           'media_id': media_id
                           }

                self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

                with self.session.post(f'https://upload.twitter.com/1.1/media/upload.json', data=payload,
                                       timeout=20) as response:

                    print(response.text)
                    return response.json()['media_id']

    def Update_profile_image(self, media_id):

        payload = {'include_profile_interstitial_type': '1',
                   'include_blocking': '1',
                   'include_blocked_by': '1',
                   'include_followed_by': '1',
                   'include_want_retweets': '1',
                   'include_mute_edge': '1',
                   'include_can_dm': '1',
                   'include_can_media_tag': '1',
                   'include_ext_has_nft_avatar': '1',
                   'include_ext_is_blue_verified': '1',
                   'include_ext_verified_type': '1',
                   'skip_status': '1',
                   'return_user': 'true',
                   'media_id': str(media_id)}

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        with self.session.post('https://api.twitter.com/1.1/account/update_profile_image.json', data=payload,
                               timeout=20) as response:
            print(response.text)

    def Update_profile_banner(self, media_id):

        payload = {'include_profile_interstitial_type': '1',
                   'include_blocking': '1',
                   'include_blocked_by': '1',
                   'include_followed_by': '1',
                   'include_want_retweets': '1',
                   'include_mute_edge': '1',
                   'include_can_dm': '1',
                   'include_can_media_tag': '1',
                   'include_ext_has_nft_avatar': '1',
                   'include_ext_is_blue_verified': '1',
                   'include_ext_verified_type': '1',
                   'skip_status': '1',
                   'return_user': 'true',
                   'media_id': str(media_id)}

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        with self.session.post('https://api.twitter.com/1.1/account/update_profile_banner.json', data=payload,
                               timeout=20) as response:
            print(response.text)

    def Update_profile_data(self, name, description, location):

        payload = {'displayNameMaxLength': 50,
                   'name': name,
                   'description': description,
                   'location': location}

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        with self.session.post('https://api.twitter.com/1.1/account/update_profile.json', data=payload,
                               timeout=20) as response:
            print(response.text)

    def Change_password(self, password, new_password):

        payload = {'current_password': password,
                   'password': new_password,
                   'password_confirmation': new_password}

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        with self.session.post('https://api.twitter.com/i/account/change_password.json', data=payload,
                               timeout=10) as response:
            print(response.text)

    def Change_username(self):

        nicks = []
        with open('dop_data/genereg_nicks.txt', 'r') as file:
            for i in file:
                nicks.append(i.strip('\n'))

        valid_status = False

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        while valid_status == False:

            params = {'full_name': 'Adrian Wood',
                      'suggest': 'true',
                      'username': random.choice(nicks)}

            with self.session.get('https://api.twitter.com/i/users/username_available.json', params=params,
                                  timeout=10) as response:
                print(response.text)
                username = params['username']

                if response.json()['valid'] == True:
                    valid_status = True

                time.sleep(2)

        # input()

        payload = {'include_mention_filter': 'true',
                   'include_nsfw_user_flag': 'true',
                   'include_nsfw_admin_flag': 'true',
                   'include_ranked_timeline': 'true',
                   'include_alt_text_compose': 'true',
                   'screen_name': username}

        with self.session.post('https://api.twitter.com/1.1/account/settings.json', data=payload,
                               timeout=10) as response:

            print(response.text)

        return username

    def generate_password(self):
        length = random.randint(8, 12)  # длина пароля от 8 до 12 символов
        letters = string.ascii_lowercase  # все строчные буквы
        password = ''.join(random.choice(letters) for i in range(length))  # случайный пароль
        password = password[:random.randint(1, length - 1)] + random.choice(string.ascii_uppercase) + password[
                                                                                                      length - 1:]  # добавляем одну большую букву в случайное место
        return password

    def Get_my_data(self, id):

        with self.session.get(f'https://api.twitter.com/graphql/OXXUyHfKYZ-xLx4NcL9-_Q/UserTweets?variables=%7B%22userId%22%3A%22{id}%22%2C%22count%22%3A40%2C%22includePromotedContent%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3Atrue%2C%22withSuperFollowsUserFields%22%3Atrue%2C%22withDownvotePerspective%22%3Afalse%2C%22withReactionsMetadata%22%3Afalse%2C%22withReactionsPerspective%22%3Afalse%2C%22withSuperFollowsTweetFields%22%3Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D&features=%7B%22responsive_web_twitter_blue_verified_badge_is_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Afalse%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22vibe_api_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Afalse%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Afalse%2C%22interactive_text_enabled%22%3Atrue%2C%22responsive_web_text_conversations_enabled%22%3Afalse%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D', timeout=15) as response:
            data = response.json()['data']['user']['result']['timeline_v2']['timeline']['instructions'][1]['entries']['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']
            print(data['favourites_count'], data['followers_count'], data['name'], data['statuses_count'])
            return data['favourites_count'], data['followers_count'], data['name'], data['statuses_count']





    #
    #
    # Основные функции полных операций

    def Twitter_giveaway(self, id, text = '', tag = 0):

        self.Like(id)

        time.sleep(random.randint(100, 900)/100)

        self.Retweet(id)
        self.comment = None

        if text != '':

            if tag != 0:

                all_nicks = []
                with open('nicknames.txt', 'r') as file:
                    for i in file:
                        all_nicks.append(i.strip('\n'))

                comment = ''
                while comment.count('@') != tag:
                    nick = random.choice(all_nicks)
                    if nick in comment:
                        continue

                    comment+=f'@{nick} '

                self.comment = text +'\n'+ comment

            else:

                self.comment = text


        else:

            all_nicks = []
            with open('nicknames.txt', 'r') as file:
                for i in file:
                    all_nicks.append(i.strip('\n'))

            comment = ''
            while comment.count('@') != tag:
                nick = random.choice(all_nicks)
                if nick in comment:
                    continue

                comment += f'@{nick} '

            self.comment = text + '\n' + comment

        if self.comment != None:
            self.Reply(id, self.comment)



    def Twitter_warming(self):

        print(f'Прогрев аккаунта {self.name} начался')

        connections = self.Get_Connects()

        for i in range(1, random.randint(5, 17)):
            connect = random.choice(connections)

            status = self.Follow(connect)
            if status == 'ban':
                return

            time.sleep(random.randint(100,350)/100)



        connections = self.Get_Tweets()

        for i in range(1, random.randint(8, 17)):

            try:
                connect = random.choice(connections)

                self.Like(connect)
                time.sleep(random.randint(100, 230) / 100)
            except:
                pass

        tweets = []

        with open('dop_data/tweets.txt', 'r') as file:
            ff = 0
            text = ''
            for f in file:

                if '====================================================' in f:
                    ff = 1
                    if text != '':
                        # print(text)
                        # print('-----------------------------------------------')
                        tweets.append(text)
                        text = ''

                elif ff == 1 and '\n' == f:
                    ff = 0
                else:
                    text += (f)
                    ff = 0

        self.Tweet(random.choice(tweets))

        print(f'Прогрев аккаунта {self.name} закончился')

    def Twitter_warming_first_time(self, current_password):

        names = []
        with open('dop_data/genereg_names.txt', 'r') as file:
            for i in file:
                names.append(i.strip('\n'))

        descriptions = []
        with open('dop_data/genered_descriptions.txt', 'r') as file:
            ff = 0
            text = ''
            for f in file:

                if '------------------------------------------' in f:
                    ff = 1
                    if text != '':
                        # print(text)
                        # print('-----------------------------------------------')
                        descriptions.append(text)
                        text = ''

                elif ff == 1 and '\n' == f:
                    ff = 0
                else:
                    text += (f)
                    ff = 0

        tweets = []
        with open('dop_data/tweets.txt', 'r') as file:
            ff = 0
            text = ''
            for f in file:

                if '====================================================' in f:
                    ff = 1
                    if text != '':
                        # print(text)
                        # print('-----------------------------------------------')
                        tweets.append(text)
                        text = ''

                elif ff == 1 and '\n' == f:
                    ff = 0
                else:
                    text += (f)
                    ff = 0

        new_name = random.choice(names)
        new_description = random.choice(descriptions)
        new_password = self.generate_password()



        connections = self.Get_Connects()

        for i in range(1, random.randint(5, 17)):
            connect = random.choice(connections)

            status = self.Follow(connect)
            if status == 'ban':
                return

            time.sleep(random.randint(100, 350) / 100)



        new_username = self.Change_username()
        self.Update_profile_data(name = new_name,
                                 description=new_description,
                                 location='')

        time.sleep(random.randint(100, 550) / 100)



    def Access(self):

        with self.session.get('https://twitter.com/account/access', timeout=10, allow_redirects=False) as response:

            time.sleep(3)

            print(response.text)
            print(response.status_code)

        # with self.session.get('https://twitter.com/account/access', timeout=10, allow_redirects=True) as response:
        #
        #     print(response.text)
        #     print(response.headers)
        #     print(response.status_code)

    def Get_User_Id(self, name):

        with self.session.get(f'https://api.twitter.com/1.1/users/show.json?screen_name={name}', timeout=10, allow_redirects=True) as response:

            return response.json()['id_str']

    def Get_User_Followers(self, name):

        with self.session.get(f'https://api.twitter.com/1.1/users/show.json?user_id={name}', timeout=10, allow_redirects=True) as response:
            # print(response.text)
            return response.json()['followers_count']

    def add_visions(self, id):

        payload = {'sub_topics': '/tweet_engagement/1636671004352151552',
                   'unsub_topics': ''}

        with self.session.post(f'https://api.twitter.com/1.1/live_pipeline/update_subscriptions',data = payload, timeout=10) as response:
            time.sleep(1)
            pass

    def SearchTweets(self):

        payload = {'q': "NFT",
                   'lang': 'en',
                   'result_type': 'recent',
                   'count': 100
                   }

        with self.session.get('https://api.twitter.com/1.1/search/tweets.json', params=payload, timeout=10) as response:
            # print(response.text)
            return response.json()

    def GetFullTweetInfo(self, id_):


        payload = f'variables=%7B%22focalTweetId%22%3A%22{id_}%22%2C%22with_rux_injections%22%3Afalse%2C%22includePromotedContent%22%3Atrue%2C%22withCommunity%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3Atrue%2C%22withBirdwatchNotes%22%3Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D&features=%7B%22blue_business_profile_image_shape_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22vibe_api_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Afalse%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Afalse%2C%22interactive_text_enabled%22%3Atrue%2C%22responsive_web_text_conversations_enabled%22%3Afalse%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D'

        with self.session.get(f'https://twitter.com/i/api/graphql/wNNG8DBB8EaXw1lq4vFWGA/TweetDetail?{payload}', timeout=10) as response:

            print(response.json())

            try:

                full_text = \
                response.json()['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries'][0][
                    'content']['itemContent']['tweet_results']['result']['legacy']['full_text']

                # print(full_text[-3:])
                if full_text[-3:] == '...':

                    try:
                        full_text = full_text[:-3] + \
                                    response.json()['data']['threaded_conversation_with_injections_v2']['instructions'][
                                        0]['entries'][0]['content']['itemContent']['tweet_results']['result']['legacy'][
                                        'retweeted_status_result']['result']['note_tweet']['note_tweet_results'][
                                        'result']['text']
                    except:
                        pass

                elif full_text[-1] == '…':

                    try:
                        full_text = full_text[:1] + \
                                    response.json()['data']['threaded_conversation_with_injections_v2']['instructions'][
                                        0]['entries'][0]['content']['itemContent']['tweet_results']['result']['legacy'][
                                        'retweeted_status_result']['result']['note_tweet']['note_tweet_results'][
                                        'result']['text']
                    except:
                        pass

                try:
                    mediaId = response.json()['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries'][0][
                    'content']['itemContent']['tweet_results']['result']['legacy']['extended_entities']['media'][0]['id_str']

                    mediaUrl = response.json()['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries'][0][
                    'content']['itemContent']['tweet_results']['result']['legacy']['extended_entities']['media'][0]['media_url_https']

                    img_data = requests.get(mediaUrl).content

                    with open(f'{os.getcwd()}/media/{mediaId}{mediaUrl[-4:]}', 'wb') as handler:
                        handler.write(img_data)

                    return full_text, mediaId

                except:

                    return full_text, None

            except:

                return None, None




