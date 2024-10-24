import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def fetch_isbns(username, password, label,retail, monthly, rising):
    # 设置Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # 打开登录页面
        driver.get('https://www.openbookscan.com.cn')

        # 等待页面加载
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'basic_userName')))

        # 输入用户名和密码
        username_input = driver.find_element(By.ID, 'basic_userName')
        password_input = driver.find_element(By.ID, 'basic_userPwd')

        # 输入你的用户名和密码
        username_input.send_keys(username)  # 使用传入的用户名
        password_input.send_keys(password)   # 使用传入的密码

        # 提交登录表单
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # 等待登录后的页面加载
        WebDriverWait(driver, 10).until(EC.url_contains('/dashboard'))

        # 打开搜索页面
        driver.get('https://www.openbookscan.com.cn/dashboard/editor/rankingtop/bestsaller')

        # 等待搜索页面加载
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[span[text()="社科"]]')))

        # 点击社科按钮
        social_science_button = driver.find_element(By.XPATH, f'//button[span[text()="{label}"]]')
        social_science_button.click()

        # 点击传入的按钮
        if retail:
            retail_button = driver.find_element(By.XPATH, f'//button[span[text()="{retail}"]]')  # 点击零售按钮
            retail_button.click()

        if monthly:
            monthly_button = driver.find_element(By.XPATH, f'//button[span[text()="{monthly}"]]')  # 点击月按钮
            monthly_button.click()

        if rising:
            rising_button = driver.find_element(By.XPATH, f'//button[span[text()="{rising}"]]')  # 点击飙升榜按钮
            rising_button.click()

        # 点击查询按钮
        search_button = driver.find_element(By.XPATH, '//button[span[text()="查询"]]')
        search_button.click()

        # 等待查询按钮的特定属性变化为"false"
        WebDriverWait(driver, 100).until(
            lambda d: d.find_element(By.XPATH, '//button[span[text()="查询"]]')\
                .get_attribute("ant-click-animating-without-extra-node") == "false"
        )

        # 等待查询结果加载
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.ant-table-cell")))

        # 查找包含ISBN的所有元素
        isbn_elements = driver.find_elements(By.CSS_SELECTOR, "td.ant-table-cell")

        isbns = []
        names = []
        contents = []
        i = 0

        # 提取ISBN和名称
        for element in isbn_elements:
            if element.text:  # 过滤掉空文本
                if i % 12 == 1:
                    isbns.append(element.text)
                if i % 12 == 3:
                    names.append(element.text)
                    # print(i)
                    book_link = driver.find_element(By.XPATH, f'//a[@title="   {element.text}"]')

                    # 使用 JavaScript 点击元素
                    driver.execute_script("arguments[0].click();", book_link)
                    # 保存书的简介
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))  # 等待新窗口打开
                    driver.switch_to.window(driver.window_handles[1])  # 切换到新窗口

                    # 在新页面上等待“详细信息”按钮可点击
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[span[text()="详细信息"]]'))
                    )

                    # 找到“详细信息”按钮并点击
                    detail_button = driver.find_element(By.XPATH, '//button[span[text()="详细信息"]]')
                    detail_button.click()
                    # 等待详细信息加载并提取内容
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="remarkcontext"]'))
                    )

                    # 提取并保存内容
                    content_div = driver.find_element(By.XPATH, '//div[@class="remarkcontext"]')
                    content = content_div.text
                    contents.append(content if content else "")  # 即使内容为空，也要存储
                    print(content)
                    print("----已记录---", len(names), "条")
                    # 关闭新窗口
                    driver.close()
                    # 切换回主窗口
                    driver.switch_to.window(driver.window_handles[0])
                if len(names) == 200:
                    break
            i += 1

        return isbns, names, contents

    finally:
        # 关闭浏览器
        driver.quit()

# 使用示例
username = '18515589565'  # 替换为你的用户名
password = '123456'       # 替换为你的密码
label = '社科'
retail = '零售'
monthly = '月'
rising = '飙升榜'

isbns, names ,contents= fetch_isbns(username, password, label,retail, monthly, rising)
# 保存到CSV文件
label_retail_monthly_rising = f'{label}_{retail}_{monthly}_{rising}'
data = {
    'ISBN': isbns,
    'Name': names,
    'Content': contents
}
df = pd.DataFrame(data)
df.to_csv(f'{label_retail_monthly_rising}.csv', index=False, encoding='utf-8-sig')  # 以 UTF-8 编码保存 CSV 文件

print("数据已成功保存为 CSV 文件。")
