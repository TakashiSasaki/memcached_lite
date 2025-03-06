import httpimport

# GitHub の raw URL
github_raw_url = "https://raw.githubusercontent.com/TakashiSasaki/memcached_lite/refs/heads/master"

# remote_repo() の第1引数を修正
with httpimport.remote_repo(github_raw_url, ["memcached_lite"]):
    import memcached_lite

# サーバ起動のテスト
memcached_lite.stop()
