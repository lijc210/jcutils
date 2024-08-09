import requests


def fetch_docker_tags(repository, page_size=100):
    base_url = f"https://registry.hub.docker.com/v2/repositories/{repository}/tags/"
    tags = []
    page = 1

    while True:
        print(f"Fetching page {page}...")
        # 构建请求 URL
        url = f"{base_url}?page={page}&page_size={page_size}"
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功

        data = response.json()
        tag_list = data.get("results", [])
        tags.extend(tag["name"] for tag in tag_list)

        if data.get("next") is None:
            break

        page += 1

    return tags


# 使用示例
repository = "bitnami/kafka"
tags = fetch_docker_tags(repository)
for tag in tags:
    print(tag)
