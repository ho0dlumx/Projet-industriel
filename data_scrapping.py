import requests
from googlesearch import search
import os

# Function to perform the Google search
def google_search(query, num_results=200):
    results = search(query, num_results)
    search_results = []

    # Find links in the search results
    for result in results:  # Only <a> inside <div id="search">
        if result.endswith(".pdf"):  # Filter only PDF files
            search_results.append(result)
    return search_results

# Function to download the PDFs
def download_pdfs(pdf_urls, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for idx, url in enumerate(pdf_urls):
        try:
            response = requests.get(url, stream=True, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            })
            if response.status_code == 200:
                filename = os.path.join(output_folder, f"DPEF_{idx + 1}.pdf")
                with open(filename, 'wb') as pdf_file:
                    pdf_file.write(response.content)
                print(f"Downloaded successfully: {filename}")
            else:
                print(f"Failed to download {url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    queries = ["site:.fr \"DPEF 2022\" filetype:pdf", "site:.fr \"DPEF 2023\" filetype:pdf"]
    pdf_links = []

    for query in queries:
        print(f"Searching for: {query}")
        found_links = google_search(query)
        print(f"{len(found_links)} links found for the query '{query}'.")
        pdf_links += found_links

    # Remove duplicates
    pdf_links = list(set(pdf_links))
    print(f"{len(pdf_links)} unique links found.")

    # Download the PDFs
    if pdf_links:
        download_pdfs(pdf_links, output_folder="DPEF_PDFs")
    else:
        print("No PDFs found for download.")
