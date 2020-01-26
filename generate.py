import urllib.request
import lxml.etree
import urllib.parse
import email.utils
import datetime
import zipfile
import io
# import pytz


class UTC3(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=3)

    def tzname(self, dt):
        return "UTC+3"

    def dst(self, dt):
        return datetime.timedelta(hours=3)


def to_excel_date(date):
    delta = date - datetime.datetime(1900, 1, 1) + datetime.timedelta(days=1)
    return delta.days if delta.days < 60 else delta.days + 1  # Feb 29 bug https://support.microsoft.com/en-us/kb/214326


def validate(xmlparser, xmlfilename):
    try:
        with open(xmlfilename, 'r') as f:
            lxml.etree.fromstring(f.read(), xmlparser)
        return True
    except lxml.etree.XMLSchemaError:
        return False


def main():
    FILES_URL = 'http://pmetro.su/Files.xml'
    FILES_FILENAME = 'Files.xml'
    NEW_FILES_FILENAME = 'NewFiles.xml'
    DOWNLOAD_URL = 'http://pmetro.su/download'
    # TIMEZONE = pytz.timezone('Europe/Moscow')
    TIMEZONE = UTC3()
    SCHEMA_FILENAME = 'Files.xsd'

    # download Files.xml
    try:
        urllib.request.urlretrieve(FILES_URL, FILES_FILENAME)
    except:
        print('Cannot download url {} to file {}'.format(FILES_URL, FILES_FILENAME))
        return
    # validate Files.xml
    with open(SCHEMA_FILENAME, 'r') as f:
        schema_root = lxml.etree.XML(f.read())
    schema = lxml.etree.XMLSchema(schema_root)
    xmlparser = lxml.etree.XMLParser(schema=schema)
    try:
        tree = lxml.etree.parse(FILES_FILENAME, xmlparser)
        encoding = tree.docinfo.encoding
    except lxml.etree.LxmlError as e:
        print('Xml file {} doesn\'t match schema {}'.format(FILES_FILENAME, SCHEMA_FILENAME))
        print(e)
        return

    # try:
    #     tree = xml.etree.ElementTree.parse(FILES_FILENAME)
    #     filelist = tree.getroot()
    # except Exception:
    #     print('Cannot parse xml file {}'.format(FILES_FILENAME))
    #     return
    filelist = tree.getroot()

    update_available = False
    # for each scheme request .zip from server
    for file in filelist.findall('File'):
        zip_xml = file.find('Zip')
        name_xml = zip_xml.attrib['Name']
        date_xml = zip_xml.attrib['Date']
        url = urllib.parse.urljoin(DOWNLOAD_URL, name_xml)
        try:
            response = urllib.request.urlopen(url)
        except:
            print('Cannot open url {}'.format(url))
            return
        try:
            date_http = email.utils.parsedate_to_datetime(response.getheader('Last-Modified'))
        except:
            print('Cannot get date and time from HTTP response')
            return
        date_http_local = date_http.astimezone(TIMEZONE).replace(tzinfo=None)
        if int(date_xml) > to_excel_date(date_http_local):
            print('Error: file {} has more recent entry in {} than its modification date'.format(name_xml, FILES_FILENAME))
        elif int(date_xml) < to_excel_date(date_http_local):
            print('Update available for {}: {}'.format(name_xml, date_http_local.date()))
            zip_xml.attrib['Date'] = str(to_excel_date(date_http_local))

            zip_archive = zipfile.ZipFile(io.BytesIO(response.read()), 'r')
            pmz_xml = file.find('Pmz')
            pmz_name = pmz_xml.attrib['Name']
            info = zip_archive.NameToInfo[pmz_name]
            if int(pmz_xml.attrib['Date']) > to_excel_date(datetime.datetime(*info.date_time)):
                print('Error: file {} has more recent entry in {} than its modification date'.format(pmz_name, FILES_FILENAME))
            elif int(pmz_xml.attrib['Date']) < to_excel_date(datetime.datetime(*info.date_time)):
                print('\tUpdate available for {}: {}'.format(pmz_name, datetime.datetime(*info.date_time).date()))
                # print('Old date: {}, new date: {}'.format(pmz_xml.attrib['Date'], to_excel_date(datetime.datetime(*info.date_time))))
                pmz_xml.attrib['Date'] = str(to_excel_date(datetime.datetime(*info.date_time)))
            update_available = True

    if update_available:
        filelist.attrib['Date'] = str(to_excel_date(datetime.datetime.now()))
        tree.write(NEW_FILES_FILENAME, encoding=encoding)


if __name__ == '__main__':
    main()
