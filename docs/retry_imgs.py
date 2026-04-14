import urllib.request, os, time

DOCS = r"C:\Users\User\Documents\Claude Code Test\docs\img"

images = {
    "kael_portrait.png":  "https://r.miro.com/6000000000/170216/160/373/1/original.png?response-content-disposition=attachment%3B%20filename%3D%22Gemini_Generated_Image_tb36ptb36ptb36pt.png%22%3B%20filename%2A%3DUTF-8%27%27Gemini_Generated_Image_tb36ptb36ptb36pt.png&Expires=1776119226&Signature=GLaDinj2gg2nwgu9h8s2wmAGvwZpSpYnvtv6T8pbFmPhoHfjQMM8eCK1-XRCS6~qrBTo-5ONf3tj8kz2oyeKF1k97Kzjhim5Krb3j-7iSSWctA7CoNKPmYfya2xEIwYontDAfAwajs3RI2pF45~0Q1r7yjUd46z8DelIqM9iA5eLuYgZfKEWUCRgQZ09IgjD~J7C-MPrIDok~G6vANUsfO523NfbDaq0TY6~Syck0i743wUSkqzE19IobsyOYbr8bAIuvi2Gdzu5TtB5e-p2iXNiCki6R1JjrC2PVo~gXlwNnx3jUIcP3iEmBkp3a~7tGDJ1OaQZUSQFbssevM24yg__&Key-Pair-Id=K2SFWAA7M8EHSK",
    "world_map.png":      "https://r.miro.com/6000000000/170222/145/154/1/original.png?response-content-disposition=attachment%3B%20filename%3D%22image.png%22%3B%20filename%2A%3DUTF-8%27%27image.png&Expires=1776119226&Signature=nESGIuHm0wowjnrmHkQgRSA9hXu1V4yPNf08ggBQnYultL4ubcQp2G5eLU7rg2WXCJZQ5mMrWyd9Yj4xeGswqXBp80y8SZA7gTMikQ7LOeBY1q62u2zJ2fHu4ZpRSPjHonuoBa6HtpV08CBDBwO6zNvODNglC3vwt21L4Li0l2q9ZM3x-rydhDyNdZTteuvWDfXucWclsPj2AfZP-dSCBC7O8-N-aOdPAWNULyL7BdTC-7ClFWszwW9f8uRMBSlNn4yMF9kupALhgoqtDdC8S5kg5xCKlq2EDTG-q3rNKiBjz88GyusFeggiT-zB6mDhUVTwTXPmN~GAa3xjwvcwzw__&Key-Pair-Id=K2SFWAA7M8EHSK",
    "continent_02_a.png": "https://r.miro.com/6000000000/170222/145/134/1/original.png?response-content-disposition=attachment%3B%20filename%3D%22ea2c9ea7-e8f8-4459-99a8-53952ecfe6d3.png%22%3B%20filename%2A%3DUTF-8%27%27ea2c9ea7-e8f8-4459-99a8-53952ecfe6d3.png&Expires=1776119227&Signature=gHeCpyImxQ7j5fEdR9ZrZqAoCZ5MflS0qDO7CfGH2dAHexXhwMuCwUV01PY2P~cIN9vEPel9xqVkUBhzEd~X4XVOPy~RYa7MibiSkKWxuT2b06m~6w4f5o7urCHu7q9QXQoIj0OM4qc5Xm2gaArGW-kTCZhUlxXXO41raIrxyh3nbeAtLOA6pMijaEoREDuZ65MlblbxnEPy~KXm-6Kgjpz8z~YQj1Fk9C7NCK-PDAtwG9TygANhgPOFl2Jhc7yi3s3UuQPp~Ln5I2B-Usi4BQ5~f3tHIMF0CrG4mffK8Ss-Eux~fh5Q9fWwC2M2qhTZAyTUoRZ9xhq~04M3DEhVrA__&Key-Pair-Id=K2SFWAA7M8EHSK",
    "continent_05_b.png": "https://r.miro.com/6000000000/170221/145/21/1/original.png?response-content-disposition=attachment%3B%20filename%3D%221afcd0ba-1d7d-4388-9336-6ebcb7b6e1d6.png%22%3B%20filename%2A%3DUTF-8%27%271afcd0ba-1d7d-4388-9336-6ebcb7b6e1d6.png&Expires=1776119227&Signature=MJFMLNB2Hn1M3cH2RMyKA7NpC2Jkl2jcPR7pEvOV-zJoeG9N8hR5WOuYlN1nyHLK18jf8ttI-i9Xc1RIaHuhU6YHZ-UBRzvd67UeNw4IiF3xVRXyFC0aL6R7VDqlEVWXK5c~C6k5tr4xmOCKoIXYg0CUZTBD5v2vY4l3l702WSnEZnMW9nQKrJZ9ZNXFVGomgZlcY1OSpqRPrArTkhGC6ZL4dLvgncjWg1nOic3k7~GRQ41ckNYrcZoev45ubsZyBi~lIlpc3UylOqyw4WSaU3S3CT5xDpHKfbmq3iXO3cSC~72OHRijLeZljbguI5OJRoxtV5fmrRheVLfTQvGZxQ__&Key-Pair-Id=K2SFWAA7M8EHSK",
    "battle_menu_02.png": "https://r.miro.com/6000000000/170222/53/365/1/original.png?response-content-disposition=attachment%3B%20filename%3D%22image.png%22%3B%20filename%2A%3DUTF-8%27%27image.png&Expires=1776119228&Signature=LsOhNGPEm-ifAwmOqFmxyi8jboXQtz87G5gNz9LylEFuQwmCQkkncTSNwGeVyBt1o7KpJdxZik~Bqh0byuGwzxBpoeDR5byW9DFKSmzUTesYbzD6Pis8YCynUdYtGFl-4Ns7rpnuPhlmj~9yh4qX0pWSRYCIp76-OhWX~UQC-TJFRZLDOZupj1ADqDS6bb4tzkIhlk1ivH9e5HDIN0Vtlo1IeAEXFTGnpB9RwGtA8e4zLLdrt8b5WY5b8tahQ770lAn-~PMmF6K6dFvg3lmFXBM1Vvp-T3zIpwK5oDKJy15HtWBoRTyOzdBR57zb47ymeh-9r7Oh3bzwy99h5YBWVQ__&Key-Pair-Id=K2SFWAA7M8EHSK",
    "battle_anim_01.png": "https://r.miro.com/6000000000/170221/122/172/1/original.png?response-content-disposition=attachment%3B%20filename%3D%22image.png%22%3B%20filename%2A%3DUTF-8%27%27image.png&Expires=1776119228&Signature=kv-b6KoQV~6uLqXMQTsydyVAytgIqM-4VRblETZt5QK9XrFmNS4NNfV6WNvN8UDKf-7nId1SfAb1lVhyaapMscrAevoJqP-Pg~hv7hmzqt3nQ-lK2qrurhfBNIVkYWCXVbzVMtm0vnCExxCkvIKnPRWmj0BrCGyVEuzXbv3G~-4u~9I4i5OmWw~TlX~9l-mxMq7Z6YvW4eFB~qL7btIP1DKgNzQe7piJ69pLRG-8wgoZY-X7Lv8PrFdT2IMHTSQ0jsg10WoSDZZpPoo3wjCwCTmz0ShFpRDArhmFqLLIqS6aczv0PZjyDqKs7fAG-MYxAH5~74-JSaxy1Q7I9B0oGA__&Key-Pair-Id=K2SFWAA7M8EHSK",
    "battle_anim_02.png": "https://r.miro.com/6000000000/170221/122/202/1/original.png?response-content-disposition=attachment%3B%20filename%3D%22image.png%22%3B%20filename%2A%3DUTF-8%27%27image.png&Expires=1776119229&Signature=D3vD33V8Vo7DWiHfAfVjCnjng8gEJ6nuO~5K36Pt0h2VwbuRGA7wulE3x-R5blrkcsvjFxHr3WwDeUPqdjXzkM7jeFRibqkIzBhbif0isu2JpD2asX1hOziaFz~m6ypuYxITcIeWtnA8~oEKAWChySstAQNa74YzFeeZEAy11rCbF90cMLjhKV-jT9Pu6l5ByUbL3jVbil2ILcvVYqiHAZMPEyyytvLQQqqKmyrvN8ScTCkwsGOoh2PK5oqWVbV9kinU1gqy5BVgFaz2r8V7L~ExsNXWltXTNYjKr2Fy5pLIvMnALwj8yRPRr1zyhgtqaWZesBBujNR6ok8bSfz3jA__&Key-Pair-Id=K2SFWAA7M8EHSK",
}

req_headers = {"User-Agent": "Mozilla/5.0"}
for name, url in images.items():
    path = os.path.join(DOCS, name)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
                f.write(r.read())
            size = os.path.getsize(path)
            print(f"OK ({size:,} bytes): {name}")
            break
        except Exception as e:
            print(f"Attempt {attempt+1} FAIL: {name} — {e}")
            time.sleep(2)
