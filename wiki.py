from wikipedia import summary, page, search 

summary_text = input("Enter the topic you want to search on Wikipedia: ")
try:
    result = summary(summary_text, sentences=5)
    print("\nSummary:\n", result)
    page_title = search(summary_text)[0]
    wiki_page = page(page_title)
    print("\nFull Page URL:\n", wiki_page.url)
except Exception as e:
    print("An error occurred:", e)
    
    