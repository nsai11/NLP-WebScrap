#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 16:28:41 2020
Create an output CSV file with area, job title, company, experience,
salary, location, description, tags associated, posting date, scraping date. 
@author: nsai
"""

from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from csv import DictReader
from urllib.parse import urlparse
from datetime import date

## Using Selenium with BeautifulSoup as using just BeautifulSoup is causing Captcha issues
## Cannot independently use Selenium as there are no unique XPaths, hence use of both Selenium and BS4 is necessary

#Variables to print

scraping_date= 0
pages = 0
driver =  webdriver.Chrome("/Users/nsai/Documents/Research/chromedriver")

#Function to get Soup from the web page

def get_soup(url):
    driver =  webdriver.Chrome("/Users/nsai/Documents/Research/chromedriver")
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    driver.close()
    return soup

#Function to scrape all parameters from the web page
    
def extract_all(soup,area):
    
    global pages
   
    areas = []
    scrape_date = []
    
    jobTitles = []  #Scrape Job Titles
    for title in soup.find_all('a', {'class': 'title fw500 ellipsis'}): 
        titleText = title.text
        jobTitles.append(titleText)

    companyTitles = []  #Scrape Company Name
    for company in soup.find_all('a',{'class': 'subTitle ellipsis fleft'}):
        companyText = company.text
        companyTitles.append(companyText)

    experience = [] #Scrape Experience
    for exp in soup.find_all('li',{'class': 'fleft grey-text br2 placeHolderLi experience'}):
        experienceText = exp.text
        experience.append(experienceText)

    salary = [] #Scrape Salary
    for sal in soup.find_all('li',{'class': 'fleft grey-text br2 placeHolderLi salary'}):
        salaryText = sal.text
        salary.append(salaryText)

    description = []    #Scrape Job Description
    for jd in soup.find_all('div',{'class' : 'job-description fs12 grey-text'}):
        jdText = jd.text
        description.append(jdText)

    tags = []   #Scrape tags
    for t in soup.find_all('ul',{'class' : 'tags has-description'}):
        tags_sub = []
        for t1 in t:
            tags_sub.append(t1.text)
        tags.append(tags_sub)
   
    dates = []  #Scrape Date of posting job
    for d in soup.find_all('div',{'class' : 'type br2 fleft grey'}):
        dText = d.text
        dates.append(dText)
    
    # Loop to populate area for job
    r = len(list(zip(jobTitles,companyTitles,experience,salary,description,tags,dates)))
    for i in range(0,r,1):
        areas.append(area)
    
    #Loop to populate scrape date
    for j in range(0,r,1):
        scrape_date.append(date.today())
    
    #Extracting number of posts and dividing the number of posts by 20 to get number of pages
    num_posts = soup.find('span',{'class' : 'fleft grey-text mr-5 fs12'})
    np = num_posts.text[-4:]
    pages = int(np,10)//20
    df1 = pd.DataFrame(list(zip(areas,jobTitles,companyTitles,experience,salary,description,tags,dates,scrape_date)))
    return df1

#Function to loop through all pages for a job posting
    
def page_loop(url,area):
    base_url = urlparse(url)
    print(url)
    for i in range(2, pages):
        newurl = base_url._replace(path = base_url.path + "-" + str(i))
        try:
            soup = get_soup(newurl.geturl())
            df1 = extract_all(soup,area)
            print(newurl.geturl())
            print(df1)
            df1.to_csv("/Users/nsai/Documents/Research/task2.csv", mode = "a")
        except:
            continue

## Looping through the given csv and creating a Pandas DataFrame to store the results in a csv
    
with open("/Users/nsai/Downloads/OneDrive_1_30-04-2020/link_by_areas.csv","r") as read_obj:
    csv_dict_reader = DictReader(read_obj)
    for row in csv_dict_reader :
        soup = get_soup(row['link'])
        df = extract_all(soup,row['type'])
        print(df)
        df.to_csv("/Users/nsai/Documents/Research/task2.csv", mode = "a",header = ["Area","Job Title","Company","Experience",
                    "Salary","Job Description","Tags","Posting Date","Scraping Date"])
        page_loop(row['link'],row['type'])
        
       
        
        
       
        
        
        
    
