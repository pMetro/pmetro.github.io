import lxml.etree
import datetime
import os
import zipfile

# Update Files.xml

MAP_DIR = 'download'
SCHEMA_FILENAME = 'Files.xsd'
FILES_FILENAME = 'Files.xml'
NEW_FILES_FILENAME = 'NewFiles.xml'


def to_excel_date(date):
    delta = date - datetime.datetime(1900, 1, 1) + datetime.timedelta(days=1)
    return delta.days if delta.days < 60 else delta.days + 1  # Feb 29 bug https://support.microsoft.com/en-us/kb/214326


def validate(xml_parser, xml_filename):
    try:
        with open(xml_filename, 'r') as f:
            lxml.etree.fromstring(f.read(), xml_parser)
        return True
    except lxml.etree.XMLSchemaError:
        return False


# def check_zip(zip_name, pmz_name, pmz_size):
#     zip_archive = zipfile.ZipFile(MAP_DIR + os.sep + zip_name, 'r')
#     info_pmz = zip_archive.NameToInfo[pmz_name]
#     if pmz_size != info_pmz.file_size:
#         print('Size differ')
#         return True
#     return False


def check_file(file, i):
    zip_xml = file.find('Zip')
    zip_name = zip_xml.attrib['Name']
    zip_size = zip_xml.attrib['Size']
    zip_date = zip_xml.attrib['Date']
    pmz_xml = file.find('Pmz')
    pmz_name = pmz_xml.attrib['Name']
    pmz_size = int(pmz_xml.attrib['Size'])
    pmz_date = pmz_xml.attrib['Date']
    city_xml = file.find('City')
    city_name = city_xml.attrib['Name']
    city_cname = city_xml.attrib['CityName']
    city_country = city_xml.attrib['Country']
    print('{:3} zip name - {:12} size - {} date - {}'.format(i, zip_name, zip_size, zip_date))
    print('    pmz name - {:12} size - {} date - {}'.format(pmz_name, pmz_size, pmz_date))
    print('   city name - {:12} cityName - {} country - {}'.format(city_name, city_cname, city_country))
    if city_name != '':  # ignore not maps records
        zip_archive = zipfile.ZipFile(MAP_DIR + os.sep + zip_name, 'r')
        info_pmz = zip_archive.NameToInfo[pmz_name]

        if pmz_size != info_pmz.file_size:
            pmz_xml.attrib['Date'] = str(to_excel_date(datetime.datetime(*info_pmz.date_time)))  # TODO
            return True
    return False


def main():
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

    file_list = tree.getroot()

    update_available = False
    # for each scheme request .zip from server
    i = 1
    for file in file_list.findall('File'):
        if check_file(file, i):
            update_available = True
        i = i + 1

    if update_available:
        file_list.attrib['Date'] = str(to_excel_date(datetime.datetime.now()))
        tree.write(NEW_FILES_FILENAME, encoding=encoding)


if __name__ == '__main__':
    main()
