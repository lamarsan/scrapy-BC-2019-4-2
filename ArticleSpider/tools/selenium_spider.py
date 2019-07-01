import time
from selenium import webdriver

# 完成微博模拟登陆
driver = webdriver.Chrome(r'D:\chromedriver_win32\chromedriver')

driver.get("https://www.weibo.com")
time.sleep(15)

driver.find_element_by_css_selector("#loginname").send_keys("asdwzepeng@163.com")
driver.find_element_by_css_selector(".info_list.password input[name ='password']").send_keys("la08xhya%(")
driver.find_element_by_css_selector(".info_list.login_btn a[node-type = 'submitBtn']").click()
