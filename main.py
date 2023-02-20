import time
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from datetime import date
import mysql.connector
from mail import send_email
from smtplib import SMTPAuthenticationError


if __name__ == '__main__':
    # define page number
    page_number = 1

    # connect to mysql
    db = mysql.connector.connect(user='web_scraping_user',
                                 password='!@#123qwe',
                                 host='localhost',
                                 database='web_scraping')

    # run code for each page
    while True:

        # get page html content
        # post data
        post_data = urlencode({
            '__EVENTARGUMENT': f'Page${page_number}',
            '__EVENTTARGET': 'ctl00$ctl00$ctl00$ctl00$ContentPlaceHolderDefault$INWMasterContentPlaceHolder$INWPageContentPlaceHolder$ucNoticeResult$lvNoticeList'
        }).encode()
        # page url
        url = 'https://publishednotices.asic.gov.au/browsesearch-notices/'
        # make request
        req = Request(url, data=post_data)
        page = urlopen(req)
        html = page.read().decode("utf-8")
        print(f'data for page {page_number}')

        # use bs4 for parsing html
        soup = BeautifulSoup(html, "html.parser")

        # get html table info
        # companies table id
        table_id = 'ContentPlaceHolderDefault_INWMasterContentPlaceHolder_INWPageContentPlaceHolder_ucNoticeResult_lvNoticeList'

        # get list of all table rows for processing
        table_rows = list(soup.select(f'#{table_id} > tr'))

        # if we reached to last page reset page number
        if len(table_rows) == 0:
            page_number = 0

        # get each notice info
        for row in table_rows:
            record = {}

            # if row is in recognized format
            try:
                # get notice
                title = str(row.select('h3'))[1:-1].replace('<h3>', '').replace('</h3>', '').replace('<br/>', ' - ').replace('  ', ' ')
                record['notice_title'] = title.replace('"', "'")
                # get published date
                temp = list(map(int, str(row.select('div .published-date')).split('</span>')[1].split('</div>')[0].split('/')))
                published_date = date(temp[2], temp[1], temp[0])
                record['published_date'] = published_date
                # get company name
                company_name = str(row.select('p > p'))[4:-5].replace('<span>', '').replace('</span>', '')
                record['company_name'] = company_name.replace('"', "'")
                # get company ACN and status
                temp = list(row.select('p > dl > dd'))
                company_ACN = str(temp[0])[4:-5]
                record['company_ACN'] = company_ACN.replace('"', "'")
                company_status = str(temp[1])[4:-5]
                record['company_status'] = company_status.replace('"', "'")
                # get notice link
                notice_link = row.a['href']
                record['notice_link'] = notice_link.replace('"', "'")
                print(record)

                # select query for searching if record is already in db
                search_query = f'''
                    SELECT * FROM `notices`
                    WHERE `notice_title` = "{record['notice_title']}" AND `company_ACN` = "{record['company_ACN']}"
                '''
                cursor = db.cursor()
                cursor.execute(search_query)
                search_result = cursor.fetchall()

                # if record is already in db
                if len(search_result) != 0:
                    # update status if current record is more recent
                    if record['published_date'] > search_result[0][2]:
                        update_record = f'''
                            UPDATE `notices`
                            SET `company_status` = "{record['company_status']}"
                            WHERE `notice_title` = "{record['notice_title']}" AND `company_ACN` = "{record['company_ACN']}"
                        '''
                        cursor.execute(update_record)
                        db.commit()

                # if record is not in db
                else:
                    # add to db
                    add_record = f'''
                        INSERT INTO `notices`
                        (`id`, `notice_title`, `published_date`, `company_name`, `company_ACN`, `company_status`, `notice_link`) 
                        VALUES (NULL, "{record['notice_title']}", "{record['published_date']}", "{record['company_name']}", 
                        "{record['company_ACN']}", "{record['company_status']}", "{record['notice_link']}");
                     '''
                    cursor.execute(add_record)
                    db.commit()

                    # email notification
                    # make email body
                    email_body = f'''
                    This is a liquidation notification.
                    The company {record['company_name']} with {record['company_ACN']} company number was added for liquidation on {str(record['published_date'])}.
                    '''
                    # make email recipients
                    recipients = ['s.ghomeshi@yahoo.com']
                    # send email
                    try:
                        send_email(email_body, recipients)
                    # could not authenticate
                    except SMTPAuthenticationError:
                        print('could not authenticate')

            # if row is useless data
            except IndexError:
                pass

        # add page number
        page_number += 1
        # sleep for each iteration
        time.sleep(10)
