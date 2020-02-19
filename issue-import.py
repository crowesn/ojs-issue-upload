# ojs issue import processor

import pandas as pd
import re
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


########################
#
#
#  Setting up functions
#
#
########################

def issue_xml(articles): # accepts articles cluster
    # take 2nd row and pull issue numbers, etc for xml
    issue_all_data = articles[2:3]

    # issue_all_data['Volume'].values[0].astype(int)
    volume = issue_all_data.Volume.values[0].astype(int) # required
    number = issue_all_data.Number.values[0].astype(int) # required
    year = issue_all_data.Year.values[0].astype(int) # required
    page = issue_all_data.Page.values[0]

    #access status should eq 1 for open access, 2 for subscription

def parse_authors(authors):
        if pd.notnull(authors):
            authors = list(filter(None, re.split(', |and ', authors)))
            author_xml = '' # instantiate holder for xml string
            for author in authors:
                a = author.split() # split into first and last
                if len(a) < 2:
                    break
                author_xml += f"""<author include_in_browse="true" user_group_ref="Author">
                    <firstname>{a[0]}</firstname>
                    <lastname>{a[1]}</lastname>
                    <email>jalcaeditor@gmail.com</email>
                  </author>
                """
            return author_xml

def article_xml(article):
    def authors_xml(article):
        authors = parse_authors(article.Author)
        return authors


    def submission_number():
        # mint a consecutive submission number
        pass

    number = submission_number # required
    volume = int(article.Volume) # required
    number = int(article.Number) # required
    year = int(article.Year) # required
    #page = int(article.Page)
    title = article.Title # required
    abstract = article.Abstract
    authors = authors_xml(article)
    filename = article.Filename
    
######################
#
#
# Doin the work
#
#
######################


# ingest csv
df = pd.read_csv('article_upload.csv', sep=',')

# get unique list of issue numbers, exclude Nan
uniq_issues = set((df['Volume'].dropna().astype(str) + df['Number'].dropna().astype(str)))

for issue in uniq_issues:

    issue_all_data = df.loc[(df['Volume'].astype(str)+df['Number'].astype(str)) == issue][2:3]

    # get value from column
    # issue_all_data['Volume'].values[0].astype(int)

    articles = df.loc[(df['Volume'].astype(str)+df['Number'].astype(str)) == issue]

    # process issue level xml
    issue_xml(articles) # write to file
    
    # process article level xml
    for index, article in articles.iterrows():
        article_xml(article) # write to file


