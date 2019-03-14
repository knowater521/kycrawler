from bs4 import BeautifulSoup
import requests
import pymysql

baseUrl = 'https://yz.chsi.com.cn'
# url = 'https://yz.chsi.com.cn/sch/'

# https://yz.chsi.com.cn/zsml/queryAction.do?dwmc=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6
# https://yz.chsi.com.cn/zsml/querySchAction.do?ssdm=&dwmc={}&mldm=&mlmc=%E9%97%A8%E7%B1%BB--&yjxkdm=&xxfs=&zymc=


def save_school_info(school_id, school, majors):

    print("开始写数据库")
    print(school_id, school)
    conn = pymysql.connect(host="localhost", port=3306, user="root", password="wang0302", db="graduate")
    cursor = conn.cursor()
    cursor.execute('insert into school values (%s,%s,%s,%s,%s)', (str(school_id), school["name"], school["location"], school["subjection"], school["speciality"]))
    print("学校写数据库完毕，开始写专业数据")

    for index in range(1, len(majors)):
        major = majors[index]

        sql = "select * from department where school_id=%d and name='%s'" % (school_id, major["department"])
        cursor.execute(sql)
        if len(cursor.fetchall()) <= 0:
            cursor.execute('insert into department (name, school_id) values (%s,%s)', (major["department"], str(school_id)))
        cursor.execute('select * from department where school_id=%s and name=%s', (str(school_id), major["department"]))
        department_id = cursor.fetchall()[0][0]

        cursor.execute('select * from major where department_id=%s and name=%s', (str(department_id), major["major"]))
        if len(cursor.fetchall()) <= 0:
            cursor.execute('insert into major (name, department_id) values (%s,%s)', (major["major"], str(department_id)))

    print("专业写数据库完毕")
    conn.commit()
    conn.close()

def get_school_page_num(start):

    url = 'https://yz.chsi.com.cn/sch/?start={}'.format(start)
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    number = soup.select('body > div.main-wrapper > div.container > div.yxk-table > div > div > form > ul > li:nth-child(8) > a')[0].text
    return int(number)

def get_all_school_info(start):

    page_number = get_school_page_num(start)

    for each_number in range(0, page_number):

        print('获取学校数据：从' + str(start) + '开始，第' + str(each_number) + '页')

        url = 'https://yz.chsi.com.cn/sch/?start={}'.format(start + each_number * 20)

        wb_data = requests.get(url)
        soup = BeautifulSoup(wb_data.text, 'lxml')

        tbody_soup = soup.select('tbody')[0]
        tr_soup = tbody_soup.find_all("tr")

        for index in range(0, len(tr_soup)):
            td_soup = tr_soup[index].find_all("td")
            school_info = get_school_detail_info(td_soup)
            print(str(index) + '.' + school_info['name'])

            majors = get_school_major_info(school_info['name'])
            print(school_info, majors)

            save_school_info(1 + start + each_number * 20 + index, school_info, majors)

def get_school_detail_info(school):

    school_dict = {}
    for index in range(0, len(school)):
        td = school[index]

        if 0 == index:
            a_soup = td.select('a')[0]
            school_dict['name'] = a_soup.text.replace(' ', '').replace('\r\n', '')
        elif 1 == index:
            school_dict['location'] = td.text
        elif 2 == index:
            school_dict['subjection'] = td.text
        elif 3 == index:
            speciality = []
            for text in td.stripped_strings:
                speciality.append(text)
            school_dict['speciality'] = ','.join(speciality)
        else:
          continue

    return school_dict

def get_school_major_page_num(school_name):

    url = 'https://yz.chsi.com.cn/zsml/querySchAction.do?ssdm=&dwmc={}&mldm=&mlmc=&yjxkdm=&xxfs=&zymc='.format(school_name)
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    if len(soup.select('li.lip.lip-input-box.clearfix.lip-last')) > 0:
        number = int(soup.select('li.lip.lip-input-box.clearfix.lip-last')[0].previous_sibling.previous_sibling.select('a')[0].text)
    else:
        number = int(soup.select('li.lip.lip-last')[0].previous_sibling.select('a')[0].text)
    return number

def get_school_major_info(school_name):

    page_num = get_school_major_page_num(school_name)
    print(school_name + '一共' + str(page_num) + '页专业')

    major_list = []
    for num in range(1, page_num + 1):
        majors = get_school_major_detail_info(num, school_name)
        print(school_name + '获取专业数据：第' + str(num) + '页')
        major_list = major_list + majors

    return major_list

def get_school_major_detail_info(page_num, school_name):

    url = 'https://yz.chsi.com.cn/zsml/querySchAction.do?ssdm=&dwmc={}&mldm=&mlmc=&yjxkdm=&xxfs=&zymc='.format(school_name)
    wb_data = requests.post(url, data={'pageno': page_num})
    soup = BeautifulSoup(wb_data.text, 'lxml')

    tbody_soup = soup.select('tbody')[0]
    tr_soup = tbody_soup.find_all("tr")

    major_list = []
    for tr in tr_soup:
        td_soup = tr.find_all("td")

        major_dict = {}
        for index in range(0, len(td_soup)):
            td = td_soup[index]

            if 1 == index:
                major_dict['department'] = td.text
            elif 2 == index:
                major_dict['major'] = td.text

        major_list.append(major_dict)

    return major_list


get_all_school_info(0)

# get_school_major_info('北京大学')


# wb_data = requests.get(url)
# soup = BeautifulSoup(wb_data.text, 'lxml')
# number = soup.select('body > div.main-wrapper > div.container > div.yxk-table > div > div > form > ul > li:nth-child(8) > a')[0].text
# # get_page_link(int(number))
# get_page_link(1)
#
# conn = pymysql.connect(host="localhost", port=3306, user="root", password="wang0302", db="graduate")
# cursor = conn.cursor()
#
# cursor.execute('delete from school')
# for index in range(1, len(schoolInfo) + 1):
#     info = schoolInfo[index - 1]
#     print(index, info["name"], info["location"], info["subjection"], info["speciality"], info["link"])
#     cursor.execute('insert into school values (%s,%s,%s,%s,%s,%s)', (index, info["name"], info["location"], info["subjection"], str(info["speciality"]), info["link"]))
#     conn.commit()
#     print('插入第' + str(index) + '条')
# conn.close()





