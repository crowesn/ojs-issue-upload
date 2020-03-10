# ojs issue import processor

import pandas as pd
import re
import html

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

global access_status, uploader

article_count = 99999999 # set initial int for incrementing local ids
input_file = 'open_access_upload.xlsx' # set input file here
access_status = '1' # access status should eq 1 for open access, 2 for subscription
uploader = 'ojsadmin' # account associated with submission


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
    number = "{:02d}".format(issue_all_data.Number.values[0].astype(int)) # required
    issue_all_data.Number.values[0].astype(int) # required
    year = issue_all_data.Year.values[0].astype(int) # required

    def generate_issue_metadata_xml(*arg):
        return f"""<issue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" published="1" current="1" access_status="{access_status}">
    <id type="internal" advice="ignore">74</id>
    <description locale="en_US">&lt;p&gt;JALCA {volume}({number})</description>
    <issue_identification>
      <volume>{volume}</volume>
      <number>{number}</number>
      <year>{year}</year>
      <title locale="en_US">Journal of the American Leather Chemists Association</title>
    </issue_identification>
    <date_published>{year}-{number}-01</date_published>
    <last_modified>2020-03-09</last_modified>
    <sections>
      <section ref="jt" seq="3" editor_restricted="0" meta_indexed="1" meta_reviewed="0" abstracts_not_required="0" hide_title="0" hide_author="0" abstract_word_count="0">
        <id type="internal" advice="ignore">87</id>
        <abbrev locale="en_US">jt</abbrev>
        <policy locale="en_US">&lt;p&gt;Complete text of journal&lt;/p&gt;</policy>
        <title locale="en_US">Journal text</title>
      </section>
      <section ref="FM" seq="2" editor_restricted="0" meta_indexed="0" meta_reviewed="0" abstracts_not_required="1" hide_title="0" hide_author="0" abstract_word_count="0">
        <id type="internal" advice="ignore">86</id>
        <abbrev locale="en_US">FM</abbrev>
        <policy locale="en_US">&lt;p&gt;Journal cover, advertisements, and other material&lt;/p&gt;</policy>
        <title locale="en_US">Front Matter</title>
      </section>
      <section ref="ART" seq="1" editor_restricted="0" meta_indexed="1" meta_reviewed="1" abstracts_not_required="0" hide_title="0" hide_author="0" abstract_word_count="0">
        <id type="internal" advice="ignore">85</id>
        <abbrev locale="en_US">ART</abbrev>
        <title locale="en_US">Articles</title>
      </section>
      <section ref="ll" seq="4" editor_restricted="0" meta_indexed="1" meta_reviewed="1" abstracts_not_required="0" hide_title="0" hide_author="0" abstract_word_count="0">
        <id type="internal" advice="ignore">88</id>
        <abbrev locale="en_US">ll</abbrev>
        <policy locale="en_US">&lt;p&gt;Author Biographies&lt;/p&gt;</policy>
        <title locale="en_US">Lifelines</title>
      </section>
    </sections>
    <issue_galleys xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://pkp.sfu.ca native.xsd"/>
        """
    issue_xml = generate_issue_metadata_xml(issue_id,volume,year,number)
    return issue_xml

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

    def generate_abstract(article):
        if pd.isna(article.Abstract):
            return ''
        return html.escape(html.unescape(f"""<abstract locale="en_US">{article.Abstract}</abstract>"""))

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
        return f"""<submission_file xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" stage="proof" id="{article_count}" xsi:schemaLocation="http://pkp.sfu.ca native.xsd">
          <revision number="1" genre="Article Text" filename="{filename}.pdf" viewable="false" date_uploaded="2020-01-27" date_modified="2020-01-27" filesize="596590" filetype="application/pdf" user_group_ref="Journal manager" uploader="{uploader}">
            <name locale="en_US">ojsadmin, Journal manager, {filename}.pdf</name>
            <href src="/tmp/files/{filename}.pdf"></href>
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
      <article xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" locale="en_US" date_submitted="{year}-01-01" stage="production" date_published="{year}-{month}-01" section_ref="{section_ref}" seq="1" access_status="{access_status}">
        <title locale="en_US">{title}</title>
        {abstract}
        <copyrightHolder locale="en_US">Journal of the American Leather Chemists Association</copyrightHolder>
        <copyrightYear>{year}</copyrightYear>
        {authors_xml}
        {submission_xml}
        {pages}
      </article>"""

    def get_pages(pages):
        if pd.isna(pages):
            return ''
        return f"""<pages>{pages}</pages>"""

    article_counter() #increment count for internal id

    month = "{:02d}".format(article.Number) # required
    number = generate_submission_number(article)# required
    section_ref = article.Section # need section e.g. ART for articles, etc
    volume = int(article.Volume) # required
    year = int(article.Year) # required
    pages = get_pages(article.Page)
    title = article.Title # required
    abstract = generate_abstract(article)
    authors_xml = generate_authors_xml(article)
    submission_xml = generate_file_submission_xml(article.Filename)
    xml = generate_article_metadata_xml(pages,article_count,month,section_ref,volume,year,title,abstract,authors_xml,submission_xml)
    return xml
    

######################
#
#
# Doin the work
#
#
######################


# ingest csv
df = pd.read_excel(input_file, sep=',')

# open file for output
out = open('out-open.xml', 'w')

# get unique list of issue numbers, exclude Nan
uniq_issues = sorted(set((df['Volume'].dropna().astype(str) + df['Number'].dropna().astype(str))))

out.write(f"""<?xml version="1.0"?>
<issues xmlns="http://pkp.sfu.ca" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://pkp.sfu.ca native.xsd">""")

for issue in uniq_issues:
    issue_all_data = df.loc[(df['Volume'].astype(str)+df['Number'].astype(str)) == issue][2:3]
    # get value from column
    # issue_all_data['Volume'].values[0].astype(int)

    articles = df.loc[(df['Volume'].astype(str)+df['Number'].astype(str)) == issue]

    # process issue level xml
    #out.write(issue_xml(articles, issue)) # write to file
    out.write(issue_xml(articles, issue)) # write to file
    # process article level xml
    out.write(f"""<articles xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://pkp.sfu.ca native.xsd">""")
    for index, article in articles.iterrows():
        out.write(article_xml(article))  #write to file
    out.write("</articles></issue>")
out.write("</issues>")

out.close()
