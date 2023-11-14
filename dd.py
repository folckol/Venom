def Tweet(self, text, mediaId=None):
    if mediaId == None:

        payload = {"variables": {
            "tweet_text": text,
            "dark_request": False,
            "media": {
                "media_entities": [],  # {'media_id': ..., 'tagged_users': []}
                "possibly_sensitive": False
            },
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True,
            "withSuperFollowsUserFields": True,
            "semantic_annotation_ids": []
        }, "features": {
            "tweetypie_unmention_optimization_enabled": True,
            "vibe_api_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "interactive_text_enabled": True,
            "responsive_web_text_conversations_enabled": False,
            "responsive_web_twitter_blue_verified_badge_is_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": False,
            "verified_phone_label_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": False,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        },
            "queryId": "Tz_cZL9zkkY2806vRiQP0Q"
        }

        with self.session.post("https://api.twitter.com/graphql/Tz_cZL9zkkY2806vRiQP0Q/CreateTweet", json=payload,
                               timeout=30) as response:

            print(response.text)

    else:

        payload = {"variables": {
            "tweet_text": text,
            "dark_request": False,
            "media": {
                "media_entities": [{'media_id': str(self.Upload_image(f'{mediaId}.jpg')), 'tagged_users': []}],
                # {'media_id': ..., 'tagged_users': []}
                "possibly_sensitive": False
            },
            "semantic_annotation_ids": []
        }, "features":
            {"tweetypie_unmention_optimization_enabled": True,
             "vibe_api_enabled": True,
             "responsive_web_edit_tweet_api_enabled": True,
             "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
             "view_counts_everywhere_api_enabled": True,
             "longform_notetweets_consumption_enabled": True,
             "tweet_awards_web_tipping_enabled": False,
             "interactive_text_enabled": True,
             "responsive_web_text_conversations_enabled": False,
             "longform_notetweets_rich_text_read_enabled": True,
             "blue_business_profile_image_shape_enabled": True,
             "responsive_web_graphql_exclude_directive_enabled": True,
             "verified_phone_label_enabled": False,
             "freedom_of_speech_not_reach_fetch_enabled": False,
             "standardized_nudges_misinfo": True,
             "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
             "responsive_web_graphql_timeline_navigation_enabled": True,
             "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
             "responsive_web_enhance_cards_enabled": False},
            "queryId": "7TKRKCPuAGsmYde0CudbVg"
        }

        self.session.headers.update({'content-type': 'application/json'})
        with self.session.post("https://api.twitter.com/graphql/7TKRKCPuAGsmYde0CudbVg/CreateTweet", json=payload,
                               timeout=30) as response:

            print(response.text)