# ojs issue import processor

import pandas as pd
import re
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

article_count = 99999999 # set initial int for incrementing local ids

########################
#
#
#  Setting up functions
#
#
########################

def issue_xml(articles, issue): # accepts articles cluster
    # take 2nd row and pull issue numbers, etc for xml
    issue_all_data = articles[2:3]

    # issue_all_data['Volume'].values[0].astype(int)
    issue_id = issue.replace('.', '') #required
    volume = issue_all_data.Volume.values[0].astype(int) # required
    number = issue_all_data.Number.values[0].astype(int) # required
    year = issue_all_data.Year.values[0].astype(int) # required
    page = issue_all_data.Page.values[0]

    #access status should eq 1 for open access, 2 for subscription

def parse_authors(authors):
    authors = list(filter(None, re.split(', |and ', authors)))
    author_xml = '<authors xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://pkp.sfu.ca native.xsd">' # instantiate holder for xml string
    for author in authors:
        a = author.split() # split into first and last
        if len(a) < 2:
            break
        author_xml += f"""<author include_in_browse="true" user_group_ref="Author">
	    <firstname>{a[0]}</firstname>
	    <lastname>{a[1]}</lastname>
	    <email>jalcaeditor@gmail.com</email>
	  </author>"""
    author_xml += '</authors>'
    return author_xml

def article_counter():
    global article_count 
    article_count += 1
    return article_count

def article_xml(article):

    def generate_authors_xml(article):
        if pd.isna(article.Author):
            return ''
        authors = parse_authors(article.Author)
        return authors

    def generate_submission_number(article):
        return str(article.Volume) + str(article.Number)

    def generate_file_submission_xml(filename):
        if pd.isna(filename): # return nothing if filename is blank
            return ''
        return f"""<submission_file xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" stage="proof" id="{number}" xsi:schemaLocation="http://pkp.sfu.ca native.xsd">
          <revision number="1" genre="Article Text" filename="{filename}.pdf" viewable="false" date_uploaded="2020-01-27" date_modified="2020-01-27" filesize="596590" filetype="application/pdf" user_group_ref="Journal manager" uploader="ojsadmin">
            <name locale="en_US">ojsadmin, Journal manager, {filename}.pdf</name>
            <href src="/tmp/leather/{filename}.pdf"></href>
          </revision>
        </submission_file>
            <article_galley xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" approved="false" xsi:schemaLocation="http://pkp.sfu.ca native.xsd">
          <id type="internal" advice="ignore">993</id>
          <name locale="en_US">PDF</name>
          <seq>0</seq>
          <submission_file_ref id="{article_count}" revision="1"/>
        </article_galley>"""

    def generate_article_metadata_xml(*arg):
        return f"""
      <article xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" locale="en_US" date_submitted="2020-01-27" stage="production" date_published="2020-01-27" section_ref="{section_ref}" seq="1" access_status="1">
        <title locale="en_US">Identification and Characterization of Potential Biocide-Resistant Fungal Strains from Infested Leathers</title>
        <subtitle locale="en_US">{title}</subtitle>
        <abstract locale="en_US">{abstract}</abstract>
        <copyrightHolder locale="en_US">Journal of the American Leather Chemists Association</copyrightHolder>
        <copyrightYear>{year}</copyrightYear>
        {authors_xml}
        {submission_xml}
      </article>"""

    article_counter() #increment count for internal id

    number = generate_submission_number(article)# required
    section_ref = 'ART' # need section e.g. ART for articles, etc
    volume = int(article.Volume) # required
    year = int(article.Year) # required
    #page = int(article.Page)
    title = article.Title # required
    abstract = article.Abstract
    authors_xml = generate_authors_xml(article)
    submission_xml = generate_file_submission_xml(article.Filename)
    xml = generate_article_metadata_xml(article_count,section_ref,volume,year,title,abstract,authors_xml,submission_xml)
    print(xml)
    return xml

######################
#
#
# Doin the work
#
#
######################


# ingest csv
df = pd.read_csv('article_upload_test.csv', sep=',')

# get unique list of issue numbers, exclude Nan
uniq_issues = set((df['Volume'].dropna().astype(str) + df['Number'].dropna().astype(str)))

for issue in uniq_issues:

    issue_all_data = df.loc[(df['Volume'].astype(str)+df['Number'].astype(str)) == issue][2:3]

    # get value from column
    # issue_all_data['Volume'].values[0].astype(int)

    articles = df.loc[(df['Volume'].astype(str)+df['Number'].astype(str)) == issue]

    # process issue level xml
    issue_xml(articles, issue) # write to file
    
    # process article level xml
    for index, article in articles.iterrows():
        article_xml(article) # write to file


