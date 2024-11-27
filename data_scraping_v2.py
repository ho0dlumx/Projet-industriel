# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 15:26:07 2024

@author: Mehdi
"""

import requests
from bs4 import BeautifulSoup
import os
import time

# Base URL for Bing search with PDF filter for extra-financial performance declarations in 2022
base_url = "https://www.bing.com/search?q=d%C3%A9claration+de+performance+extra-financi%C3%A8re+pdf+2022"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
}

# Set up the download folder
download_folder = "DPEF_PDFs"
os.makedirs(download_folder, exist_ok=True)

# Number of pages to scrape
num_pages = 50
pdf_links = set()  # Using a set to automatically handle duplicates

# Loop through the pages
for page in range(num_pages):
    url = f"{base_url}&first={page * 10 + 1}"  # Adjust 'first' parameter for pagination
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract PDF links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):  
            pdf_links.add(href)
        if len(pdf_links) >= 280:  # Stop collecting links once we reach 280
            break
    
    # Small delay to avoid hitting the server too quickly
    time.sleep(2)

# Download each PDF
for i, pdf_link in enumerate(pdf_links):
    try:
        pdf_response = requests.get(pdf_link, headers=headers)
        pdf_path = os.path.join(download_folder, f"DPEF_{i+1}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_response.content)
        print(f"Téléchargé : {pdf_path}")
    except requests.exceptions.MissingSchema:
        print(f"Invalid URL skipped: {pdf_link}")
    except Exception as e:
        print(f"Failed to download {pdf_link}: {e}")

print(f"Total PDFs downloaded: {len(pdf_links)}")
