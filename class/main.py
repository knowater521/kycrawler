from bs4 import BeautifulSoup
import requests

baseUrl = 'https://yz.chsi.com.cn'
url = 'https://yz.chsi.com.cn/sch/'

def get_page_link(page_number):

    schoolInfo = []

    for each_number in range(0, page_number):

        print('第' + str(each_number) + '页')

        full_url = 'https://yz.chsi.com.cn/sch/?start={}'.format(each_number * 20)

        wb_data = requests.get(full_url)
        soup = BeautifulSoup(wb_data.text, 'lxml')

        tbody_soup = soup.select('tbody')[0]
        tr_soup = tbody_soup.find_all("tr")

        for tr in tr_soup:
            td_soup = tr.find_all("td")

            dict = {}
            for index in range(0, len(td_soup)):
                td = td_soup[index]

                if 0 == index:
                    a_soup = td.select('a')[0]
                    dict['name'] = a_soup.text.replace(' ', '').replace('\r\n', '')
                    dict['link'] = baseUrl + a_soup.get('href')
                elif 1 == index:
                    dict['location'] = td.text
                elif 2 == index:
                    dict['subjection'] = td.text
                elif 3 == index:
                    speciality = []
                    for text in td.stripped_strings:
                        speciality.append(text)
                    dict['speciality'] = speciality
                else:
                    break

            schoolInfo.append(dict)

    print(len(schoolInfo), schoolInfo)

wb_data = requests.get(url)
soup = BeautifulSoup(wb_data.text, 'lxml')
number = soup.select('body > div.main-wrapper > div.container > div.yxk-table > div > div > form > ul > li:nth-child(8) > a')[0].text
get_page_link(int(number))






