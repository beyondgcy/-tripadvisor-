# -tripadvisor-
爬取猫途鹰评论的酒店信息/评论信息/评论者信息
城市链接.txt内含需要爬取的城市链接
hotels_crawl.py根据这些城市链接，创建包含该城市的酒店链接的txt
tripadvisor_crawl.py根据酒店链接的txt，爬取详细内容，存入csv文件
爬取完成的csv示例见Four_Corners_Florida.csv
程序支持断点续传
